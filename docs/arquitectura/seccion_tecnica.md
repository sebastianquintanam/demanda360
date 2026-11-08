# Sección técnica · Demanda360

> Borrador para el documento final, escrito por el Rol 1 a partir del repositorio (versión 1.0). Olmer lo integra y ajusta el formato. Las cifras medidas corresponden al entorno de demostración con datos simulados.

## 1. Arquitectura

Demanda360 es una sola aplicación web (Flask) que sirve las pantallas y la API, con PostgreSQL y n8n al lado, todo en Docker Compose. El principio que ordena el diseño es que **Flask valida y registra, PostgreSQL es la única fuente de datos, n8n solo avisa y Power BI solo lee**. Ningún otro componente guarda saldos.

| Componente | Tecnología | Qué hace | Qué no hace |
| --- | --- | --- | --- |
| Web y API | Python 3.12, Flask 3, Flask-Login, Flask-WTF, SQLAlchemy, gunicorn | Valida, registra, verifica el rol en cada ruta y escribe la auditoría | No envía correos ni guarda copias de saldos |
| Base de datos | PostgreSQL 16 | Fuente oficial; restricciones, triggers y vistas de KPI | No se expone a la red (puerto atado a 127.0.0.1) |
| Automatización | n8n 2.46.6 | Recibe el evento de stock crítico y envía el correo | No calcula ni guarda inventario |
| Analítica | Power BI Desktop | Muestra los 5 KPI desde CSV exportados de las vistas | No escribe datos |
| Pantallas | HTML, CSS y JavaScript en plantillas Jinja | Dashboard, Registro y Planificación, a partir del Figma | No calculan reglas de negocio |

Diagrama: `docs/arquitectura/arquitectura_mvp.png`.

## 2. Decisiones técnicas

| Decisión | Por qué |
| --- | --- |
| El esquema vive en `01_schema.sql`, no en el ORM | La base impone las reglas aunque el backend falle, y el equipo de datos pudo escribir vistas sin esperar al backend. |
| El saldo se calcula y nunca se guarda: último conteo más movimientos posteriores | Un saldo guardado se desincroniza. Calculado, siempre coincide con el historial. |
| Historial de solo inserción (trigger) | Nadie puede borrar ni editar una venta, un conteo o la auditoría. Una corrección es un ajuste justificado o un conteo nuevo. |
| KPI con fecha de corte explícita (30 de septiembre por defecto) | Los datos demo son de septiembre. Con el corte, una venta en vivo cambia el saldo sin mover los KPI del mes. |
| Power BI lee CSV, no se conecta a la base | La base no se abre a la red y los CSV quedan versionados junto al código. |
| La alerta se crea dentro de la transacción de la venta y se envía después de confirmarla | Si n8n está caído, la venta igual se guarda y la alerta queda `FALLIDA` para reintentarla. El correo nunca deshace una venta. |
| Cada formulario envía un identificador único (`origen_ref`) | Un doble clic o un reenvío no duplica registros: la API responde `duplicado: true`. |
| Una sola automatización en n8n | Es lo mínimo que resuelve la fricción. La IA queda como propuesta. |

## 3. Modelo de datos

Son 11 tablas: usuarios, categorías, proveedores, productos, conteos físicos, movimientos, solicitudes de clientes, alertas enviadas, pedidos, detalle de pedidos y auditoría. El diagrama entidad-relación y las reglas que impone la base están en `docs/arquitectura/modelo_datos.md`, y el detalle de cada columna en el diccionario de datos.

Ninguna tabla guarda datos de clientes. Las contraseñas se guardan solo como hash (scrypt).

## 4. Reglas de negocio implementadas

**Estado de cada producto.** Se asigna un solo estado, en este orden de prioridad:

| Estado | Condición |
| --- | --- |
| Sin conteo | Nunca se ha contado; el saldo se muestra vacío, no como 0 |
| Agotado | Saldo 0 |
| Crítico | Saldo igual o menor que el umbral de reposición |
| Datos insuficientes | Menos de 30 días desde el primer conteo |
| Baja rotación | 0 a 2 unidades vendidas en 30 días |
| Normal | Ninguna de las anteriores |

**Cantidad sugerida.** `máx(0, techo(demanda de 30 días × días de cobertura / 30 − saldo))`, donde la demanda es lo vendido más lo no atendido. El cliente que regresa por lo que faltó no se cuenta dos veces. La pantalla muestra la fórmula con los números de cada producto, y el propietario decide.

**Pedidos.** `BORRADOR → APROBADO → ENVIADO → CONFIRMADO` o `CANCELADO`. Solo el propietario aprueba y cambia estados. Si un proveedor cancela, el pedido se puede reintentar **una vez** con otro proveedor. Una transición inválida responde 409.

**Alerta.** Se dispara solo cuando una venta **cruza** el umbral (el saldo pasa de estar por encima a quedar igual o por debajo). Una venta posterior, con el saldo ya bajo el umbral, no repite el correo.

## 5. API

| Ruta | Quién | Para qué |
| --- | --- | --- |
| `GET/POST /api/productos`, `GET /api/productos/{id}`, `GET /api/catalogos` | Crear: propietario · Consultar: ambos | Catálogo con saldo y estado |
| `POST /api/conteos`, `POST /api/ventas`, `POST /api/movimientos` | Ambos (el ajuste, solo el propietario) | Registro de inventario y demanda |
| `GET /api/dashboard`, `GET /api/analisis/rotacion` | Ambos | KPI 1–3 y productos críticos |
| `GET /api/sugeridos`, `GET/POST /api/pedidos`, `/aprobar`, `/estado` | Sugeridos, aprobación y estados: propietario | Planificación de pedidos |
| `GET /api/auditoria` | Propietario | Bitácora de operaciones |

Los errores responden en JSON con un código (`VALIDACION`, `SKU_DUPLICADO`, `SIN_CONTEO`, `TRANSICION_INVALIDA`…) y nunca muestran trazas internas. Contrato completo: `docs/api/contrato.md`.

## 6. Controles de seguridad

Los controles se implementan en el código y cada uno tiene una evidencia que se puede mostrar. Aplican controles de la ISO/IEC 27002 en el entorno de demostración; **no significan que Pinturas By-plus tenga un SGSI ni una certificación**.

| # | Control | Implementación | ISO/IEC 27002 | Evidencia |
| --- | --- | --- | --- | --- |
| 1 | SKU único | `UNIQUE` en la base y validación en Flask | 8.26 | SKU repetido → 409 |
| 2 | Cantidades válidas | Enteros y rangos con `CHECK` en la base | 8.26 | Cantidad inválida → 400 |
| 3 | Autenticación | Flask-Login, sesión de 8 h, cookie `HttpOnly` | 8.5 | Ruta sin sesión → 401 |
| 4 | Contraseñas con hash | scrypt con sal aleatoria (Werkzeug) | 5.17 | La tabla `usuarios` solo tiene hashes |
| 5 | Permisos por rol | Verificación en cada ruta del backend, no solo en pantalla | 5.15 | Trabajador → 403 |
| 6 | Aprobación del propietario | Solo un propietario aprueba; solo se envía lo aprobado | 5.15 | Transición inválida → 409 |
| 7 | Bitácora | Fila en `auditoria` en la misma transacción; tabla de solo inserción | 8.15 | `GET /api/auditoria` |
| 8 | Ajustes justificados | Solo el propietario; justificación de 10 a 500 caracteres; los movimientos no se borran | 8.15 | Ajuste sin justificación → 400 |
| 9 | Secretos fuera del código | `.env` excluido de Git; el token del webhook va en una cabecera | 5.17 | `.gitignore`; webhook sin token → 403 |
| 10 | Respaldo y restauración | `pg_dump` con huella SHA-256 y restauración verificada en una base aparte | 8.13 | Registro de respaldos |
| 11 | Minimización de datos | Sin datos de clientes; proveedores ficticios | 5.34 | Diccionario de datos |
| 12 | Control de versiones | `main` protegida; todo entra por pull request aprobado, con pruebas en verde | 8.32 | Historial de PR y de la CI |

Además: CSRF en todos los formularios y en los `POST` de la API, puertos atados a `127.0.0.1`, contenedor de la app sin privilegios de root y errores sin trazas.

## 7. Pruebas y calidad

- **150 pruebas automáticas** (pytest) contra un PostgreSQL 16 real: reglas de la base, autenticación, roles, validaciones, ventas, alertas y reintento, KPI con los datos demo, pedidos y pantallas (sesión, rol y lógica que carga cada una). Además, las tres pantallas se revisaron en el navegador contra la API real.
- **Integración continua:** GitHub Actions corre todas las pruebas en cada pull request y en cada merge a `main`. Todas las corridas del proyecto están en verde.
- **Datos demo verificables:** un generador con semilla fija produce el mes de septiembre, y una prueba exige que los KPI den 27,3 %, 8,6 % y 50 %. El Rol 3 los recalculó a mano en Excel.

## 8. Pruebas de integración medidas

| Prueba | Resultado (entorno de demostración) |
| --- | --- |
| Venta que cruza el umbral con n8n apagado | Venta guardada; alerta `FALLIDA` con «No se pudo conectar con n8n» |
| Reintento con n8n encendido | Mismo evento pasa a `ENVIADA` (intento 2); correo recibido; ejecución de n8n en 2,8 s |
| Segunda venta bajo el umbral | Sin alerta nueva |
| Webhook sin token | 403 |
| Respaldo y restauración (Mac) | 11 tablas, 262 filas, 11 saldos y 5 KPI iguales; restauración en 0,5 s |

El mismo evento (`evento_id`) se rastrea en la pantalla, la base, la ejecución de n8n y el correo.

## 9. Continuidad

- **Respaldo:** `scripts/backup.sh` guarda el respaldo fuera del repositorio, con permisos restringidos y una huella SHA-256 que detecta si el archivo se dañó o se modificó.
- **Restauración de prueba:** `scripts/restore_prueba.sh` restaura en una base aparte, sin tocar la principal, y compara tabla por tabla.
- **RPO de 1 hora y RTO de 4 horas:** son objetivos. Para el RPO se documenta una tarea horaria (`cron`); en la demo el respaldo se corre a mano. Solo se reporta lo medido en el entorno de prueba.

## 10. Limitaciones

- No hay línea base real: los KPI muestran cómo se mediría, no una mejora comprobada.
- El RTO y el RPO solo se midieron en el entorno de demostración.
- Las sugerencias son reglas transparentes; no hay pronóstico ni IA en el MVP.
- El umbral y el contacto del proveedor no se editan desde las pantallas.
- Es un piloto propuesto: Pinturas By-plus no lo está usando.

<!-- Para decidir en equipo: si el documento declara el uso de IA en el desarrollo, una redacción posible es:
«El código se desarrolló con apoyo de un asistente de IA (Claude Code). El equipo definió los requerimientos y las reglas del negocio, revisó cada cambio en un pull request y verificó el resultado con pruebas automáticas y pruebas de integración.» -->
