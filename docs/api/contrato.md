# Contrato de la API · Demanda360

> Fuente: plan del MVP, sección 4. Cualquier cambio en este archivo necesita la aprobación del líder técnico (Rol 1) y de pantallas (Rol 4).
> **Forma exacta de cada respuesta:** los archivos de `frontend/static/mock/`. Si un mock y este documento no coinciden, se corrige uno de los dos por PR; el backend devuelve exactamente la forma del mock.

## Estado de implementación

| Ruta | Prioridad | Estado |
| --- | --- | --- |
| `GET /api/health` | P0 | Implementada (etapa 1) |
| `GET /api/auditoria` | P0 | Implementada (etapa 1) |
| Cálculos en SQL: saldo, estado, KPI 1–5, sugeridos (`02_vistas.sql`) | P0/P1 | Implementados (etapa 2) |
| `GET/POST /api/productos`, `GET /api/productos/{id}`, `GET /api/catalogos` | P0 | Implementadas (etapa 3) |
| `POST /api/conteos`, `POST /api/ventas`, `POST /api/movimientos` | P0 | Implementadas (etapa 3) |
| `GET /api/dashboard`, `GET /api/analisis/rotacion` | P0 | Implementadas (etapa 3) |
| Alerta a n8n + `flask reintentar-alertas` | P0 | Implementada (etapa 3) |
| Sugeridos y pedidos | P1 | Etapa 5 |

## Precisiones de la etapa 1 (no cambian el plan)

- **Estados de producto** (valor exacto en JSON): `SIN_CONTEO`, `AGOTADO`, `CRITICO`, `DATOS_INSUFICIENTES`, `BAJA_ROTACION`, `NORMAL`. Clase CSS: `etiqueta-` + estado en minúsculas con guiones (`etiqueta-baja-rotacion`).
- **`saldo: null`** significa «Sin conteo». Nunca se muestra como 0.
- **Errores 500** agregan `error.referencia`, igual a la cabecera `X-Request-ID`, para encontrar el detalle en el log. Nunca traen trazas.
- **405** responde `METODO_NO_PERMITIDO` con el mismo formato.
- **CSRF inválido o ausente** en un `POST /api/*`: `400 VALIDACION` con `campos: {"csrf": "invalido"}`.
- **Sesión y rol en pantallas:** `base.html` deja el rol en `<body data-rol="...">`. Los elementos con clase `solo-propietario` se ocultan al trabajador (solo comodidad visual: el backend igual responde 403).

## Precisiones de la etapa 3 (no cambian el plan)

- **Respuestas = mocks.** Cada ruta devuelve al menos los campos de su archivo en `frontend/static/mock/`; las pruebas lo verifican. Con los datos demo, `/api/productos`, `/api/analisis/rotacion` y los críticos e inventario de `/api/dashboard` son **idénticos** a sus mocks.
- **Saldo y estado son los de hoy; los KPI son los del corte.** `GET /api/dashboard` y `/api/analisis/rotacion` aceptan `?corte=AAAA-MM-DD` (400 si el formato es inválido o la fecha es futura).
- **Un producto contado después del corte** queda en `DATOS_INSUFICIENTES` (menos de 30 días de registros), salvo que esté agotado o crítico.
- **Bloque `producto`** en las respuestas de conteo, venta y movimiento: `id`, `sku`, `saldo_anterior`, `saldo_actual`, `umbral_reposicion`, `estado`.
- **Reenvío del mismo formulario** (mismo `origen_ref`): `200` con lo que ya existe y `"duplicado": true`. Nada se registra dos veces.
- **Errores nuevos:**
  - `409 SIN_CONTEO`: entrada, ajuste o venta con entrega sobre un producto que nunca se ha contado. Una atención con `cantidad_entregada = 0` sí se registra sin conteo, porque la demanda no atendida cuenta igual.
  - `409 ORIGEN_REF_EN_USO`: ese `origen_ref` ya se usó en otro tipo de registro.
- **Ajustes:** solo el propietario (403 para el trabajador), cantidad ≠ 0 con signo, justificación de 10 a 500 caracteres y nunca un saldo negativo (409 `STOCK_INSUFICIENTE`).
- **`GET /api/catalogos`** (ambos roles): `categorias`, `proveedores` (con `plazo_entrega_dias`) y `unidades_medida`, para los formularios de Registro. Mock: `catalogos.json`.
- **Cliente que regresa:** `GET /api/productos/{id}` trae `faltantes_pendientes` (atenciones de los últimos 30 días con faltante sin cubrir). La pantalla deja escoger una y envía su `solicitud_id` como `solicitud_previa_id` en `POST /api/ventas`. Reglas: misma referencia, enlazada a la atención original (no a otro regreso) y `cantidad_solicitada` ≤ faltante pendiente; si no, 400.
- **Sin sesión:** un `POST /api/*` sin sesión responde 401 antes que el chequeo de CSRF, así una sesión vencida lleva al login.
- **KPI:** el texto explicativo de cada KPI va en `detalle` (no `nota`), como en `dashboard.json`.

## Integración de pantallas

- **Una sola copia de la lógica:** `frontend/static/js/comun.js`, `dashboard.js` y `registro.js`. Las plantillas de Flask (`frontend/templates/`) y los prototipos (`frontend/prototipo/`, con mocks) cargan los mismos archivos. Un cambio de comportamiento se hace una vez.
- **Diseño:** el Rol 4 sigue siendo dueño del prototipo y de `estilos.css`; las plantillas copian su HTML dentro de `base.html`.
- **Registro:** el formulario de producto usa `GET /api/catalogos`; el cliente que regresa escoge la atención en una lista (`faltantes_pendientes`); el conteo envía `origen_ref`; el ajuste exige 10 caracteres de justificación también en pantalla.

## Alerta de stock crítico · contrato con n8n (cerrado el 8 nov 2026)

| Paso | Qué pasa |
| --- | --- |
| 1 | Una venta hace cruzar el umbral (saldo antes > umbral ≥ saldo después). En la misma transacción se crea la fila `alertas_enviadas` en `PENDIENTE`. |
| 2 | Después del commit, Flask hace `POST` a `N8N_WEBHOOK_URL` con la cabecera `X-Demanda360-Token` y el evento de la sección 5 del plan (`evento_id`, `tipo`, `ocurrido_en`, `origen_datos`, `producto{sku, nombre, saldo, umbral, plazo_entrega_dias}`). Espera **10 s** como máximo (Gmail tarda ~2,5 s). |
| 3 | n8n responde **200 `{"ok": true, ...}` solo después de enviar el correo**; **502 `{"ok": false, "error": "..."}`** si falla el envío; 403 si el token no sirve. |
| 4 | Flask marca `ENVIADA` solo con 200 y `ok: true`. Cualquier otra cosa (502, 403, timeout, n8n apagado) → `FALLIDA`, `intentos + 1` y el motivo en `ultimo_error`. La venta nunca se deshace. |
| 5 | `flask reintentar-alertas` reenvía las `FALLIDA` (y las `PENDIENTE` de más de un minuto) con el **mismo `evento_id`**, máximo 3 intentos. Una `ENVIADA` nunca se reenvía. |

El estado vive **solo en PostgreSQL**. n8n no guarda ni descarta duplicados, porque preferimos un correo repetido a una alerta perdida. El correo incluye el `evento_id` para reconocer un repetido.

## Decisiones aprobadas (8 nov 2026)

1. **Fecha de corte de los KPI: 30 de septiembre de 2026, 23:59:59 (Bogotá).** Los KPI, la rotación y los días con registro se calculan sobre los 30 días que terminan el día de corte. En SQL el límite es «antes del 1 de octubre a las 00:00», que equivale y no pierde fracciones de segundo. El **saldo en pantalla es el de hoy** (todos los movimientos): una venta en vivo cambia el saldo, el estado y dispara la alerta, pero no mueve los KPI de septiembre. Las rutas de KPI aceptan `?corte=AAAA-MM-DD`; sin el parámetro usan `fn_corte()` (2026-09-30).
2. **Cliente que regresa: no suma demanda y conserva el faltante original.** La venta posterior se registra con `solicitud_previa_id` apuntando a la atención original. Como cada venta necesita su atención y las solicitudes son de solo inserción, en la base queda una fila de atención enlazada, marcada como regreso: no cuenta en lo solicitado ni en lo no atendido (KPI 2), y sus unidades sí cuentan como vendidas. En `POST /api/ventas` el campo `solicitud_previa_id` es opcional (etapa 3).
3. **Proveedores: un proveedor habitual por producto, con reintento a proveedores alternativos.** El plazo de entrega vive en el proveedor; la demo usa 4 proveedores ficticios (3, 4, 5 y 7 días), como en los mocks. Un pedido cancelado se puede reintentar con otro proveedor: es un pedido nuevo con `pedido_anterior_id` y `numero_intento` + 1, y alimenta el KPI 5. No hay puntuación automática de proveedores.

Cálculos oficiales (saldo, estado, KPI, sugeridos): `database/sql/02_vistas.sql`. Pruebas que exigen las cifras del Figma: `backend/tests/test_kpi_demo.py`.

---

## 4. Contrato de API

Quince rutas, diez de ellas P0. El frontend trabaja desde el primer minuto con archivos mock que tienen exactamente estas respuestas; cuando el backend esté listo, solo se cambia una variable.

### Convenciones

- Base `/api`, JSON en UTF-8, fechas ISO 8601 con zona (`-05:00`).
- **Sesión:** el login es un formulario en `/login` (Flask-Login). Una ruta `/api` sin sesión responde 401.
- **CSRF:** todo `POST` envía la cabecera `X-CSRFToken`; el token está en un `<meta>` de `base.html`.
- **Rol:** se verifica en el backend en cada ruta. Ocultar un botón no cuenta como control.
- **Sin duplicados:** el formulario genera un `origen_ref` (UUID) al abrirse. Si se reenvía, la API devuelve 200 con el registro existente en vez de crear otro.
- **Mocks:** `frontend/static/mock/*.json`, activados con `USE_MOCK = true` en `api.js`.
- **Errores:** siempre el mismo formato. Un 500 nunca muestra trazas, consultas ni credenciales.

| Código | Cuándo |
| --- | --- |
| 200 / 201 | Consulta correcta / registro creado |
| 400 `VALIDACION` | Falta un campo, cantidad no entera, negativa o fuera de rango |
| 401 `NO_AUTENTICADO` | Sin sesión |
| 403 `SIN_PERMISO` | El rol no puede hacer esa acción |
| 404 `NO_ENCONTRADO` | El producto o pedido no existe |
| 409 `SKU_DUPLICADO`, `STOCK_INSUFICIENTE`, `TRANSICION_INVALIDA` | Choca con una regla de negocio |
| 500 `ERROR_INTERNO` | Mensaje genérico; el detalle va solo al log |

### Rutas

| Método y ruta | Rol | Qué hace | Prioridad |
| --- | --- | --- | --- |
| `GET /api/health` | Público | Estado de la app y de la base | P0 |
| `GET /api/productos` | Ambos | Lista con saldo y estado | P0 |
| `POST /api/productos` | Propietario | Crea un producto | P0 |
| `GET /api/productos/{id}` | Ambos | Detalle y últimos 10 movimientos | P0 |
| `POST /api/conteos` | Ambos | Registra un conteo físico | P0 |
| `POST /api/ventas` | Ambos | Atención: solicitado y entregado; genera la venta y, si cruza el umbral, la alerta | P0 |
| `POST /api/movimientos` | Entrada: ambos · Ajuste: propietario | Entrada de mercancía o ajuste con justificación | P0 |
| `GET /api/dashboard` | Ambos | KPI y productos críticos | P0 |
| `GET /api/analisis/rotacion` | Ambos | Estado, vendidas en 30 días y cobertura por producto | P0 |
| `GET /api/auditoria` | Propietario | Últimas operaciones registradas | P0 |
| `GET /api/sugeridos?cobertura=14` | Propietario | Cantidades sugeridas con su explicación | P1 |
| `GET /api/pedidos` | Ambos | Lista de pedidos | P1 |
| `POST /api/pedidos` | Ambos | Crea un borrador | P1 |
| `POST /api/pedidos/{id}/aprobar` | Propietario | Borrador → aprobado | P1 |
| `POST /api/pedidos/{id}/estado` | Propietario | Aprobado → enviado → confirmado o cancelado (con reintento a otro proveedor) | P1 |

La ruta `POST /api/solicitudes` del contexto maestro se fusiona con `POST /api/ventas`: una atención al cliente es un solo registro.

### Ejemplos

**Crear producto** — `POST /api/productos` (valores ficticios)

```json
{
  "sku": "LAC-BP-01",
  "nombre": "Laca catalizada alto brillo galón",
  "categoria_id": 1,
  "proveedor_id": 1,
  "marca": "ColorNova (ficticia)",
  "presentacion": "Galón",
  "unidad_medida": "galon",
  "costo_compra": 85000,
  "precio_venta": 110000,
  "umbral_reposicion": 5
}
```

Respuesta `201` con el producto creado (`id`, `activo: true`, `creado_en`). Con un SKU repetido:

```json
{
  "error": {
    "codigo": "SKU_DUPLICADO",
    "mensaje": "Ya existe un producto con el SKU LAC-BP-01.",
    "campos": { "sku": "duplicado" }
  }
}
```

**Registrar una atención** — `POST /api/ventas`

```json
{
  "producto_id": 3,
  "cantidad_solicitada": 3,
  "cantidad_entregada": 2,
  "origen_ref": "9f1c2e7a-4b5d-4c1e-9a77-1d2f3e4a5b6c",
  "solicitud_previa_id": null
}
```

Respuesta `201`. Si el correo falla, `alerta.estado` llega como `FALLIDA`, pero la venta ya quedó guardada:

```json
{
  "solicitud_id": 140,
  "movimiento_id": 512,
  "no_atendida": 1,
  "producto": {
    "id": 3,
    "sku": "ESM-WH-01",
    "saldo_anterior": 4,
    "saldo_actual": 2,
    "umbral_reposicion": 3,
    "estado": "CRITICO"
  },
  "alerta": { "evento_id": "5b0e8c1d-7f2a-4e3b-9c6d-0a1b2c3d4e5f", "estado": "ENVIADA" }
}
```

Si se intenta entregar más de lo disponible: `409 STOCK_INSUFICIENTE`, con el mensaje «Saldo disponible: 2. No se puede entregar 3.»

**Dashboard** — `GET /api/dashboard` (datos simulados, cifras del Figma)

```json
{
  "corte": "2026-09-30",
  "origen_datos": "SIMULADO",
  "kpis": [
    { "codigo": "KPI1", "nombre": "Referencias agotadas", "valor": 27.3, "unidad": "%", "numerador": 3, "denominador": 11 },
    { "codigo": "KPI2", "nombre": "Demanda no atendida", "valor": 8.6, "unidad": "%", "numerador": 12, "denominador": 139 },
    { "codigo": "KPI3", "nombre": "Baja rotación", "valor": 50.0, "unidad": "%", "numerador": 5, "denominador": 10, "detalle": "5 de 10; 1 referencia con datos insuficientes" }
  ],
  "criticos": [
    { "id": 1, "sku": "LAC-BP-01", "nombre": "Laca catalizada alto brillo galón", "saldo": 0, "estado": "AGOTADO", "plazo_entrega_dias": 3 }
  ]
}
```

**Rotación** — `GET /api/analisis/rotacion` (fragmento)

```json
{
  "corte": "2026-09-30",
  "origen_datos": "SIMULADO",
  "productos": [
    { "sku": "LAC-NG-01", "nombre": "Laca nogal galón", "saldo": 9, "vendidas_30d": 1, "no_atendidas_30d": 0, "cobertura_dias": 270, "plazo_entrega_dias": 4, "estado": "BAJA_ROTACION" },
    { "sku": "LAC-TR-01", "nombre": "Laca transparente galón", "saldo": 8, "dias_con_registro": 3, "estado": "DATOS_INSUFICIENTES" }
  ]
}
```

**Sugerido (P1)** — cada línea trae su explicación:

```json
{ "sku": "LAC-BP-01", "demanda_diaria": 1.7, "cobertura_dias": 14, "saldo": 0, "sugerido": 24, "formula": "techo(1,70 × 14 − 0) = 24", "regla_version": 1 }
```

**Permiso negado** — un trabajador intenta `POST /api/pedidos/7/aprobar`:

```json
{ "error": { "codigo": "SIN_PERMISO", "mensaje": "Solo un propietario puede aprobar pedidos." } }
```
