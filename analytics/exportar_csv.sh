#!/usr/bin/env bash
# =============================================================================
# Demanda360 · Exporta las 5 vistas de Power BI a analytics/datos_demo/*.csv
#
#   ./analytics/exportar_csv.sh                    # corte por defecto (2026-09-30)
#   CORTE=2026-10-31 ./analytics/exportar_csv.sh   # otro corte
#
# Por defecto lee la base del contenedor `db` (docker compose debe estar arriba).
# Con PSQL_LOCAL=1 usa el psql del equipo y las variables PGHOST, PGUSER, PGDATABASE...
#
# Los CSV son de SOLO LECTURA para Power BI: UTF-8 con BOM (Excel muestra bien
# las tildes), separador coma, punto decimal, fechas ISO y columna origen_datos.
# Si una cifra no cuadra, se corrige la vista en database/sql/02_vistas.sql.
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

DESTINO="analytics/datos_demo"
VISTAS=(vw_inventario_actual vw_ventas_diarias vw_solicitudes vw_kpi_resumen vw_pedidos)
CORTE="${CORTE:-}"

if [[ -n "$CORTE" && ! "$CORTE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "CORTE debe tener el formato AAAA-MM-DD (por ejemplo 2026-09-30)." >&2
  exit 1
fi

psql_cmd() {
  if [[ "${PSQL_LOCAL:-0}" == "1" ]]; then
    psql -X -q -v ON_ERROR_STOP=1 "$@"
  else
    # Las credenciales se leen DENTRO del contenedor: no pasan por esta terminal
    docker compose exec -T db sh -c 'psql -X -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" "$@"' psql "$@"
  fi
}

mkdir -p "$DESTINO"
for vista in "${VISTAS[@]}"; do
  archivo="$DESTINO/${vista#vw_}.csv"
  temporal="$(mktemp)"
  printf '\357\273\277' > "$temporal"   # BOM UTF-8 (octal: funciona en el bash 3.2 del Mac)
  if [[ -n "$CORTE" ]]; then
    psql_cmd -c "SET demanda360.corte = '$CORTE'" \
             -c "COPY (SELECT * FROM $vista) TO STDOUT WITH (FORMAT csv, HEADER)" >> "$temporal"
  else
    psql_cmd -c "COPY (SELECT * FROM $vista) TO STDOUT WITH (FORMAT csv, HEADER)" >> "$temporal"
  fi
  mv "$temporal" "$archivo"
  chmod 644 "$archivo"
  filas=$(( $(wc -l < "$archivo") - 1 ))
  printf '✓ %-28s %4d filas\n' "$archivo" "$filas"
done

echo "Listo. Corte: ${CORTE:-por defecto de la base (2026-09-30)}. Datos SIMULADOS."
