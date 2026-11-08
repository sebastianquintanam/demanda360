#!/usr/bin/env bash
# shellcheck disable=SC2016  # las comillas simples son a propósito: $POSTGRES_* se expanden DENTRO del contenedor
# Demanda360 · Restauración de prueba en una base APARTE (demanda360_restore).
#
# Uso, con `docker compose up -d` corriendo:
#   scripts/restore_prueba.sh                      restaura el respaldo más reciente
#   scripts/restore_prueba.sh RUTA/archivo.dump    restaura ese respaldo
#
# Qué hace:
#   1. Verifica la huella SHA-256 del respaldo (si existe el .sha256).
#   2. Borra y crea de nuevo la base demanda360_restore. NUNCA toca la base principal:
#      el script se detiene si las dos bases se llamaran igual.
#   3. Restaura el respaldo en una sola transacción y mide cuánto tarda.
#   4. Compara la base restaurada con la principal: filas de cada tabla, saldo de cada
#      referencia y los 5 KPI al corte.
#   5. Imprime una fila lista para docs/seguridad/registro_respaldos.md.
#
# Si alguien usó la app entre el respaldo y la restauración, la comparación mostrará
# diferencias, y eso es correcto: el respaldo es una foto. Para la evidencia, corre
# backup.sh y enseguida restore_prueba.sh.
#
# RTO de 4 horas (objetivo): se compara con el tiempo medido aquí más levantar la web y verificar.

# shellcheck source=scripts/_comun.sh
source "$(dirname "$0")/_comun.sh"

BASE_PRUEBA="demanda360_restore"

exigir_db_arriba
BASE="$(nombre_base_principal)"
[ "$BASE" != "$BASE_PRUEBA" ] || falla "La base principal se llama '$BASE_PRUEBA'. Me detengo para no borrarla."

# --- 1. Elegir el respaldo y verificar su huella ---------------------------------
if [ $# -ge 1 ]; then
  ARCHIVO="$1"
else
  DIR="$(preparar_dir_respaldos)"
  # shellcheck disable=SC2012  # los nombres los genera backup.sh: sin espacios ni caracteres raros
  ARCHIVO="$(ls -1t "$DIR"/demanda360_*.dump 2>/dev/null | head -1 || true)"
  [ -n "$ARCHIVO" ] || falla "No hay respaldos en $DIR. Corre primero scripts/backup.sh"
fi
[ -s "$ARCHIVO" ] || falla "No existe o está vacío: $ARCHIVO"

echo "Restauración de prueba"
info "Respaldo:   $ARCHIVO"
info "Principal:  $BASE (solo lectura)"
info "Prueba:     $BASE_PRUEBA (se borra y se crea de nuevo)"
echo

if [ -f "$ARCHIVO.sha256" ]; then
  esperada=$(cut -d' ' -f1 < "$ARCHIVO.sha256")
  [ "$(sha256_de "$ARCHIVO")" = "$esperada" ] || falla "La huella SHA-256 no coincide: el respaldo está dañado o fue modificado."
  ok "Huella SHA-256 verificada"
else
  info "Sin archivo .sha256: no se verifica la huella."
fi

# --- 2 y 3. Base aparte y restauración medida --------------------------------------
inicio=$(ahora_ms)
psql_en postgres <<SQL
SET client_min_messages = warning;
DROP DATABASE IF EXISTS $BASE_PRUEBA WITH (FORCE);
CREATE DATABASE $BASE_PRUEBA TEMPLATE template0 ENCODING 'UTF8';
ALTER DATABASE $BASE_PRUEBA SET timezone TO 'America/Bogota';
SQL
en_db 'pg_restore -U "$POSTGRES_USER" -d "$1" --no-owner --no-privileges --single-transaction --exit-on-error' \
  "$BASE_PRUEBA" < "$ARCHIVO"
ms_restauracion=$(( $(ahora_ms) - inicio ))
ok "Restaurado en $(segundos "$ms_restauracion")"

# --- 4. Comparación con la base principal -----------------------------------------
SQL_FILAS="SELECT table_name, (xpath('/row/n/text()',
             query_to_xml(format('SELECT count(*) AS n FROM %I.%I', table_schema, table_name), false, true, '')))[1]::text
           FROM information_schema.tables
           WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
           ORDER BY 1;"
SQL_SALDOS="SELECT sku, saldo FROM vw_saldos ORDER BY sku;"
SQL_KPI="SELECT codigo, valor FROM fn_kpi_resumen(fn_corte()) ORDER BY codigo;"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
for b in "$BASE" "$BASE_PRUEBA"; do
  echo "$SQL_FILAS"  | psql_en "$b" > "$TMP/filas_$b"
  echo "$SQL_SALDOS" | psql_en "$b" > "$TMP/saldos_$b"
  echo "$SQL_KPI"    | psql_en "$b" > "$TMP/kpi_$b"
done
ms_total=$(( $(ahora_ms) - inicio ))

diferencias=0
comparar() {   # $1 = nombre del bloque, $2 = archivo base
  if diff -q "$TMP/$2_$BASE" "$TMP/$2_$BASE_PRUEBA" >/dev/null; then
    ok "$1 coinciden"
  else
    printf '✗ %s NO coinciden (principal | restaurada):\n' "$1"
    { diff "$TMP/$2_$BASE" "$TMP/$2_$BASE_PRUEBA" || true; } | sed -n 's/^</    principal:  /p; s/^>/    restaurada: /p'
    diferencias=$(( diferencias + 1 ))
  fi
}

echo
printf 'Filas por tabla:\n    %-22s %10s %11s\n' tabla principal restaurada
while IFS='|' read -r tabla n; do
  m=$(grep "^$tabla|" "$TMP/filas_$BASE_PRUEBA" | cut -d'|' -f2 || true)
  printf '    %-22s %10s %11s\n' "$tabla" "$n" "${m:--}"
done < "$TMP/filas_$BASE"
echo
comparar "Filas de las tablas" filas
comparar "Saldos de las referencias" saldos
comparar "KPI al corte" kpi

tablas=$(wc -l < "$TMP/filas_$BASE" | tr -d ' ')
filas=$(awk -F'|' '{s += $2} END {print s + 0}' "$TMP/filas_$BASE")
refs=$(wc -l < "$TMP/saldos_$BASE" | tr -d ' ')
echo "    Ejemplo de saldos (principal):"
head -3 "$TMP/saldos_$BASE" | sed 's/|/ → /; s/^/      /'

# --- 5. Resultado y fila para el registro --------------------------------------------
echo
if [ "$diferencias" -eq 0 ]; then
  resultado="Exitosa"
  ok "RESTAURACIÓN VERIFICADA: $tablas tablas, $filas filas, $refs saldos y 5 KPI iguales."
else
  resultado="Con diferencias ($diferencias bloques)"
  printf '✗ La restauración terminó, pero hay %d bloque(s) con diferencias.\n' "$diferencias"
  info "Si alguien usó la app después del respaldo, es normal: corre backup.sh y enseguida este script."
fi
info "Duración: restauración $(segundos "$ms_restauracion") · restauración + verificación $(segundos "$ms_total")"

nombre="$(basename "$ARCHIVO")"
fecha_respaldo="$(echo "$nombre" | sed -E 's/demanda360_([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})([0-9]{2}).*/\1-\2-\3 \4:\5/')"
echo
echo "Fila para docs/seguridad/registro_respaldos.md:"
echo "| Fecha del respaldo | Archivo | Fecha de la restauración | Duración restauración | Duración con verificación | Registros verificados | Resultado |"
echo "|---|---|---|---|---|---|---|"
echo "| $fecha_respaldo | \`$nombre\` | $(date '+%Y-%m-%d %H:%M') | $(segundos "$ms_restauracion") | $(segundos "$ms_total") | $tablas tablas, $filas filas, $refs saldos, 5 KPI | $resultado |"

[ "$diferencias" -eq 0 ]
