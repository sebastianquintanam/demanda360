# Demanda360

Registro de demanda y apoyo a la planificación de pedidos para **Pinturas By-plus** (Bogotá).
Proyecto integrador · Fundamentos de Sistemas de Información · Universidad EAN · 2026.

> **Principio:** Flask valida y registra; PostgreSQL es la única fuente de datos; n8n solo avisa; Power BI solo lee. Ningún otro componente guarda saldos.
> **Todo el historial es SIMULADO** y se rotula así. Pinturas By-plus no está certificada en ISO 27001: el MVP aplica controles de la norma.

| Componente | Tecnología | Dirección local |
| --- | --- | --- |
| Web y API | Flask 3 + gunicorn | http://127.0.0.1:8000 |
| Base de datos | PostgreSQL 16 | 127.0.0.1:5432 |
| Automatización | n8n | http://127.0.0.1:5678 |
| Analítica | Power BI Desktop (lee CSV de `analytics/datos_demo/`) | — |

Especificación completa: [`docs/contexto/plan_mvp_demanda360.md`](docs/contexto/plan_mvp_demanda360.md). Contrato de la API: [`docs/api/contrato.md`](docs/api/contrato.md).

---

## Arrancar con Docker (cualquier sistema)

Requisitos: Docker Desktop (Mac/Windows) o Docker Engine (Ubuntu) y Git.

```bash
# 1. Crear tu .env a partir del ejemplo (el .env nunca se sube a GitHub)
cp .env.example .env

# 2. Generar secretos y pegarlos en .env (SECRET_KEY, POSTGRES_PASSWORD, N8N_ENCRYPTION_KEY, N8N_WEBHOOK_TOKEN)
python3 -c "import secrets; print(secrets.token_urlsafe(48))"

# 3. Levantar los tres servicios (la primera vez descarga imágenes: unos minutos)
docker compose up -d --build

# 4. Ver que estén arriba: db y web deben decir "healthy"
docker compose ps

# 5. Crear los usuarios demo (pide las contraseñas sin mostrarlas, mínimo 10 caracteres)
docker compose exec web flask crear-usuarios-demo
```

Abre http://127.0.0.1:8000 e ingresa como `propietario` o `trabajador`.
Comprobación rápida: `curl http://127.0.0.1:8000/api/health` → `{"estado":"ok","bd":"ok"}`.

**Recargar la base desde cero** (los scripts de `database/sql/` solo corren cuando el volumen está vacío):

```bash
docker compose down -v      # ⚠️ BORRA la base y n8n de tu equipo. Haz respaldo antes si importa.
docker compose up -d --build
```

## Desarrollo en el Mac (Flask fuera de Docker, más rápido para iterar)

```bash
docker compose up -d db                       # solo la base
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
set -a && source .env && set +a               # carga el .env en la terminal (DB_HOST=localhost)
cd backend
flask --app run crear-usuarios-demo
flask --app run run --debug --port 8000       # recarga al guardar
```

## Datos demo y KPI

Todo el historial es **SIMULADO**: 30 días de septiembre de 2026 con las 11 referencias del Figma (127 vendidas, 12 no atendidas, 5 pedidos). Con esos datos los KPI dan 27,3 %, 8,6 % y 50 %, y el sugerido total es 54; `backend/tests/test_kpi_demo.py` lo exige.

```bash
# En una base sin productos y con los usuarios demo ya creados:
docker compose exec web flask cargar-demo        # aplica 02_vistas.sql, carga 10_demo.sql y muestra los KPI

# Si cambia 02_vistas.sql (no borra datos):
docker compose exec web flask aplicar-vistas

# CSV para Power BI (quedan en analytics/datos_demo/):
./analytics/exportar_csv.sh
```

- **Fecha de corte:** los KPI se calculan sobre el 1–30 de septiembre (`fn_corte()` = 2026-09-30). El saldo en pantalla es el de hoy, así que una venta en vivo cambia el saldo y el estado sin mover los KPI de septiembre. Otro corte: `CORTE=2026-10-31 ./analytics/exportar_csv.sh`.
- **Los datos demo no se editan a mano:** se cambia `database/seeds/generar_demo.py` y se regenera `10_demo.sql` con `python3 database/seeds/generar_demo.py`.
- **Volver a cargar desde cero** exige base vacía: `docker compose down -v` borra también n8n (exporta antes tu flujo).

## Pantallas

| Pantalla | Plantilla (Flask) | Prototipo (mocks, Live Server) | Lógica compartida |
| --- | --- | --- | --- |
| Dashboard | `frontend/templates/dashboard.html` | `frontend/prototipo/dashboard.html` | `static/js/dashboard.js` |
| Registro | `frontend/templates/registro.html` | `frontend/prototipo/registro.html` | `static/js/registro.js` |
| Planificación | `frontend/templates/planificacion.html` | `frontend/prototipo/planificacion.html` | `static/js/planificacion.js` |

Los prototipos y las plantillas cargan los mismos `static/js/comun.js` y `static/js/<pantalla>.js`. En el prototipo, «Ver como» cambia el rol.

## Alertas a n8n

La venta que cruza el umbral crea la alerta y Flask la envía a n8n después de guardar la venta. Contrato completo: `docs/api/contrato.md`.

```bash
docker compose exec web flask reintentar-alertas   # reenvía las FALLIDAS (máximo 3 intentos, mismo evento_id)
```

Evidencia de la sección 5 del plan: con n8n apagado (`docker compose stop n8n`), una venta que cruza el umbral queda guardada y su alerta `FALLIDA`. Se enciende n8n (`docker compose start n8n`), se corre el reintento y pasa a `ENVIADA`.

## Pruebas

Corren contra un PostgreSQL real (crean y recargan solas la base `demanda360_test`):

```bash
docker compose up -d db
set -a && source .env && set +a
cd backend && pytest -q
```

En GitHub corren solas en cada pull request (`.github/workflows/ci.yml`).

## Prototipos de pantallas sin backend (Rol 4)

Abre la carpeta `frontend/` en VS Code y usa **Live Server**. Las páginas de `frontend/prototipo/` incluyen `static/js/api.js`, que detecta que no hay Flask y responde con los archivos de `frontend/static/mock/`. Cuando el líder las pasa a `frontend/templates/`, usan la API real sin cambiar nada más.

## Estructura y dueños

| Carpeta | Dueño | Qué hay |
| --- | --- | --- |
| `backend/`, `database/`, `compose.yaml` | Rol 1 · Mac | App Flask, esquema SQL, vistas, datos demo, pruebas |
| `frontend/templates/`, `frontend/static/js/`, `frontend/static/mock/` | Rol 1 · Mac | Plantillas Jinja, cliente de la API, mocks |
| `frontend/prototipo/`, `frontend/static/css/`, `docs/bpmn/` | Rol 4 · Windows pantallas | Pantallas HTML desde el Figma, estilos, BPMN |
| `analytics/` (salvo `datos_demo/`), `docs/requerimientos/kpi.md`, `diccionario_datos.md` | Rol 3 · Windows datos | Verificación de KPI, Power BI, fichas |
| `automation/`, `docs/seguridad/`, `docs/evidencias/` | Rol 2 · Ubuntu | Flujo n8n, matriz de riesgos, respaldos, evidencias |
| `scripts/` | Rol 1 escribe · Rol 2 ejecuta y documenta | Respaldo y restauración |

`.github/CODEOWNERS` asigna los revisores por carpeta.

## Reglas de Git

- `main` protegida: todo entra por pull request con una aprobación y las pruebas en verde.
- Cada quien trabaja en su rama (`feature/backend`, `feature/frontend`, `feature/analytics`, `feature/automation`) y solo en sus carpetas.
- PR pequeños, al menos dos al día. Antes de cada PR, revisar el diff: nunca `.env`, contraseñas, respaldos ni capturas sin censurar.

## Seguridad (resumen de lo implementado)

Contraseñas con hash (scrypt), sesión con cookie HttpOnly y vencimiento de 8 h, CSRF en formularios y en los `POST` de la API, permisos por rol verificados en el backend, bitácora de solo inserción, movimientos inmutables (trigger), errores sin trazas, secretos solo en `.env`, puertos atados a `127.0.0.1`, app sin privilegios de root en el contenedor. Detalle y evidencias: `docs/seguridad/`.
