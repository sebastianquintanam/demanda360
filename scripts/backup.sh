#!/usr/bin/env bash
# shellcheck disable=SC2016  # las comillas simples son a propósito: $POSTGRES_* se expanden DENTRO del contenedor
# Demanda360 · Respaldo de la base principal con pg_dump (formato custom).
#
# Uso, desde cualquier carpeta del repositorio y con `docker compose up -d` corriendo:
#   scripts/backup.sh
#   BACKUP_DIR=/otra/carpeta scripts/backup.sh
#
# Qué hace:
#   1. Corre pg_dump dentro del contenedor db. Solo LEE la base: no la modifica.
#   2. Guarda demanda360_AAAAMMDD_HHMMSS.dump en ~/demanda360_respaldos (fuera del
#      repositorio; el script se niega a guardarlo dentro). Permisos 600.
#   3. Comprueba que el archivo se puede leer con pg_restore y cuenta sus tablas.
#   4. Guarda la huella SHA-256 al lado (.dump.sha256); restore_prueba.sh la verifica.
#
# RPO de 1 hora (objetivo, no medido en producción). Línea de cron documentada:
#   0 * * * * cd /ruta/a/demanda360 && scripts/backup.sh >> ~/demanda360_respaldos/backup.log 2>&1
# En la demo el respaldo se corre a mano. Los respaldos viejos no se borran solos.

# shellcheck source=scripts/_comun.sh
source "$(dirname "$0")/_comun.sh"

exigir_db_arriba
BASE="$(nombre_base_principal)"
DIR="$(preparar_dir_respaldos)"
MARCA="$(date +%Y%m%d_%H%M%S)"
ARCHIVO="$DIR/demanda360_${MARCA}.dump"
PARCIAL="$ARCHIVO.parcial"

echo "Respaldo de la base '$BASE'"
inicio=$(ahora_ms)

# Se escribe primero a .parcial: si algo falla a mitad, no queda un .dump incompleto que parezca bueno.
trap 'rm -f "$PARCIAL"' EXIT
en_db 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --compress=6' > "$PARCIAL"
[ -s "$PARCIAL" ] || falla "pg_dump no produjo datos."

tablas=$(en_db 'pg_restore --list' < "$PARCIAL" | grep -c ' TABLE DATA ' || true)
[ "$tablas" -gt 0 ] || falla "El archivo no se pudo leer con pg_restore o no tiene tablas."

mv "$PARCIAL" "$ARCHIVO"
trap - EXIT
chmod 600 "$ARCHIVO"
huella=$(sha256_de "$ARCHIVO")
printf '%s  %s\n' "$huella" "$(basename "$ARCHIVO")" > "$ARCHIVO.sha256"
duracion=$(( $(ahora_ms) - inicio ))

ok "Respaldo creado en $(segundos "$duracion")"
info "Archivo:  $ARCHIVO"
info "Tamaño:   $(du -h "$ARCHIVO" | cut -f1)"
info "Tablas:   $tablas con datos"
info "SHA-256:  ${huella:0:16}…"
echo
echo "Siguiente paso: scripts/restore_prueba.sh   (restaura este respaldo en una base aparte)"
