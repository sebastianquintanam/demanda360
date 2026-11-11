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

Especificación completa: [`docs/contexto/plan_mvp_demanda360.md`](docs/contexto/plan_mvp_demanda360.md). Contrato de la API: [`docs/api/contrato.md`](docs/api/contrato.md). Modelo de datos: [`docs/arquitectura/modelo_datos.md`](docs/arquitectura/modelo_datos.md). Sección técnica para el documento final: [`docs/arquitectura/seccion_tecnica.md`](docs/arquitectura/seccion_tecnica.md). Propuesta de IA: [`docs/arquitectura/propuesta_ia.md`](docs/arquitectura/propuesta_ia.md).

## Estado de la versión 1.0

| Alcance | Estado |
| --- | --- |
| **P0:** login con dos roles, catálogo con SKU único, conteos, ventas (solicitado y entregado), entradas, ajustes justificados, saldo y estado por producto, alerta n8n con reintento, auditoría, KPI 1–3, respaldo y restauración | Implementado y probado |
| **P1:** cantidades sugeridas, borrador de pedido, aprobación del propietario, estados del pedido con reintento a otro proveedor, KPI 4–5, CSV para Power BI | Implementado y probado |
| Pruebas automáticas | 150 pruebas contra PostgreSQL 16 real, en verde en cada PR (CI) |
| Propuesto, fuera del MVP | IA o pronóstico de demanda, edición de umbral y proveedor desde pantallas, alertas por ajustes inusuales, conexión de Power BI en vivo |

**Los 13 criterios de la demo** (contexto maestro, sección 20) y dónde se muestran:

| # | Criterio | Dónde |
| --- | --- | --- |
| 1–3 | Crear producto, rechazar SKU repetido (409), rechazar cantidad inválida (400) | `POST /api/productos` y formularios de Registro |
| 4–6 | Conteo, venta y saldo correcto | Pantalla Registro: el resultado muestra saldo antes → después |
| 7 | Cambio no autorizado bloqueado | Trabajador: ajuste o aprobación → 403. Base: `UPDATE` sobre `movimientos` → error del trigger |
| 8 | Alerta | Venta que cruza el umbral → fila `ENVIADA` y correo. Con n8n apagado: `FALLIDA` → `flask reintentar-alertas` → `ENVIADA` |
| 9–10 | Movimiento visible en los datos y KPI calculado | Dashboard de Flask, `analytics/datos_demo/*.csv` y Power BI |
| 11–12 | Respaldo y restauración | `scripts/backup.sh` y `scripts/restore_prueba.sh` |
| 13 | Consulta de auditoría | `GET /api/auditoria` como propietario |

**Limitaciones que se declaran:** no hay línea base real, así que los KPI muestran cómo se mediría y no una mejora comprobada. El RTO y el RPO solo se miden en el entorno de demostración. Las sugerencias son reglas, sin IA. El sistema se propone como piloto: Pinturas By-plus no lo usa todavía.

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

```bash
# 6. Cargar los datos demo de septiembre (imprime los KPI: 27,3 %, 8,6 %, 50 %, 4,7 h y 66,7 %)
docker compose exec web flask cargar-demo
```

> En zsh (Mac), los comentarios `#` dentro de un bloque pegado dan error. Copia solo las líneas de comando o activa `setopt interactivecomments`.

### Configurar la alerta en n8n (una vez por equipo)

1. Abre http://127.0.0.1:5678 y crea la cuenta local de n8n.
2. **Workflows → Import from File** → `automation/workflows/alerta_stock_critico.json`.
3. Nodo **Webhook** → *Credential for Header Auth* → crear una nueva: *Name* = `X-Demanda360-Token`, *Value* = el `N8N_WEBHOOK_TOKEN` de tu `.env`. Para copiarlo sin mostrarlo en pantalla:
   - Mac: `grep '^N8N_WEBHOOK_TOKEN=' .env | cut -d= -f2- | tr -d '\n' | pbcopy`
   - Ubuntu: lo mismo terminando en `xclip -selection clipboard` (`sudo apt install xclip`).
4. Nodo **Send an Email** → credencial SMTP. Con Gmail: host `smtp.gmail.com`, puerto 465, SSL activado y una **contraseña de aplicación** (no la de la cuenta). Cambia *From Email* y *To Email*, que vienen con correos de ejemplo.
5. **Publish** (arriba a la derecha). El backend usa la URL de producción `http://n8n:5678/webhook/alerta-stock-critico`; la *Test URL* no se usa.
6. Comprueba que la web llega a n8n y que el token se exige. Sin token debe responder **403**:

```bash
docker compose exec web python -c "import requests; r = requests.post('http://n8n:5678/webhook/alerta-stock-critico', json={}); print(r.status_code)"
```

**Recargar la base desde cero** (los scripts de `database/sql/` solo corren cuando el volumen está vacío):

Borra **solo** el volumen de la base y conserva n8n (flujo y credenciales). Haz `scripts/backup.sh` antes si los datos importan:

```bash
docker compose down
docker volume rm demanda360_pgdata
docker compose up -d --build
docker compose exec web flask crear-usuarios-demo
docker compose exec web flask cargar-demo
```

`docker compose down -v` borra también el volumen de n8n: tendrías que importar el flujo y crear las credenciales otra vez.

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
- **Volver a cargar desde cero** exige base vacía: ver «Recargar la base desde cero» arriba (borra solo `demanda360_pgdata`, no n8n).

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

## Respaldo y restauración

Con `docker compose up -d` corriendo, desde la carpeta del repositorio y **sin `sudo`** (con `sudo` el respaldo queda en la carpeta de root):

```bash
scripts/backup.sh
scripts/restore_prueba.sh
```

- `backup.sh` corre `pg_dump` dentro del contenedor `db`, solo lee la base principal y guarda `demanda360_AAAAMMDD_HHMMSS.dump` y su huella `.sha256` en `~/demanda360_respaldos/`, **fuera del repositorio** (con permisos 600). Para otra carpeta: `BACKUP_DIR=/ruta scripts/backup.sh`.
- `restore_prueba.sh` toma el respaldo más reciente (o el que le pases como argumento), verifica la huella, lo restaura en la base aparte `demanda360_restore` y la compara con la principal: filas de cada tabla, saldo de cada referencia y los 5 KPI. Mide la duración e imprime una fila lista para `docs/seguridad/registro_respaldos.md`. Termina con código 0 solo si todo coincide.
- La base principal nunca se modifica. `demanda360_restore` se borra y se crea de nuevo en cada corrida.
- Corre los dos seguidos. Si alguien usa la app entre el respaldo y la restauración, la comparación muestra la diferencia, y eso es correcto: el respaldo es una foto.
- RPO de 1 hora (objetivo): `0 * * * * cd /ruta/a/demanda360 && scripts/backup.sh >> ~/demanda360_respaldos/backup.log 2>&1` en `crontab -e`. En la demo el respaldo se corre a mano.

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
| `docs/arquitectura/`, `docs/api/` | Rol 1 · Mac | Arquitectura, modelo de datos, sección técnica, contrato de la API |
| `docs/requerimientos/requerimientos.md` | Rol 4 | Requerimientos RF y RNF, trazabilidad de riesgos |

`.github/CODEOWNERS` asigna los revisores por carpeta.

## Reglas de Git

- `main` protegida: todo entra por pull request con una aprobación y las pruebas en verde.
- Cada quien trabaja en su rama (`feature/backend`, `feature/frontend`, `feature/analytics`, `feature/automation`) y solo en sus carpetas.
- PR pequeños, al menos dos al día. Antes de cada PR, revisar el diff: nunca `.env`, contraseñas, respaldos ni capturas sin censurar.

## Seguridad (resumen de lo implementado)

Contraseñas con hash (scrypt), sesión con cookie HttpOnly y vencimiento de 8 h, CSRF en formularios y en los `POST` de la API, permisos por rol verificados en el backend, bitácora de solo inserción, movimientos inmutables (trigger), errores sin trazas, secretos solo en `.env`, puertos atados a `127.0.0.1`, app sin privilegios de root en el contenedor. Detalle y evidencias: `docs/seguridad/`.
