#!/usr/bin/env bash
# shellcheck disable=SC2016  # las comillas simples son a propósito: $POSTGRES_* se expanden DENTRO del contenedor
# Funciones compartidas por backup.sh y restore_prueba.sh. No se ejecuta solo.
#
# Todo pasa por `docker compose exec -T db`: se usan pg_dump, pg_restore y psql
# del contenedor (PostgreSQL 16, la misma versión de la base) y no hace falta
# instalar nada en el equipo. Dentro del contenedor la conexión es por socket
# local, así que las contraseñas no aparecen en la línea de comandos.
#
# Compatible con el bash 3.2 que trae macOS.

set -euo pipefail
umask 077   # los respaldos contienen datos y hashes de contraseñas: solo los lee el dueño

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$RAIZ"

DIR_RESPALDOS_POR_DEFECTO="$HOME/demanda360_respaldos"

info()  { printf '  %s\n' "$*"; }
ok()    { printf '✓ %s\n' "$*"; }
falla() { printf '✗ %s\n' "$*" >&2; exit 1; }

# Milisegundos desde 1970. macOS no soporta date +%N; python3 sí está en ambos sistemas.
ahora_ms() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import time; print(int(time.time() * 1000))'
  else
    echo "$(( $(date +%s) * 1000 ))"
  fi
}

# 1834 → "1,8 s"
segundos() {
  local ms=$1
  printf '%d,%d s' $(( ms / 1000 )) $(( (ms % 1000) / 100 ))
}

sha256_de() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1
  else shasum -a 256 "$1" | cut -d' ' -f1
  fi
}

exigir_db_arriba() {
  command -v docker >/dev/null 2>&1 || falla "No encuentro docker."
  if ! docker compose ps --status running --services 2>/dev/null | grep -qx db; then
    falla "El servicio db no está corriendo. Ejecuta: docker compose up -d"
  fi
}

# Ejecuta un comando dentro del contenedor db. $1 = script de sh; el resto, sus argumentos ($1, $2…).
en_db() {
  local script=$1; shift
  docker compose exec -T db sh -c "$script" _ "$@"
}

nombre_base_principal() {
  en_db 'printf %s "$POSTGRES_DB"'
}

# SQL por la entrada estándar; $1 = base. Salida sin adornos: columnas separadas por |.
psql_en() {
  en_db 'psql -X -q -At -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$1"' "$1"
}

# Carpeta de respaldos: fuera del repositorio, siempre.
preparar_dir_respaldos() {
  local dir="${BACKUP_DIR:-$DIR_RESPALDOS_POR_DEFECTO}"
  local nuevo=0
  [ -d "$dir" ] || { mkdir -p "$dir"; nuevo=1; }
  local real
  real="$(cd "$dir" && pwd -P)"
  case "$real/" in
    "$RAIZ"/*)
      [ "$nuevo" = 1 ] && rmdir "$dir" 2>/dev/null
      falla "BACKUP_DIR ($real) está dentro del repositorio. Los respaldos nunca van al repositorio." ;;
  esac
  chmod 700 "$real"
  dir="$real"
  printf '%s' "$dir"
}
