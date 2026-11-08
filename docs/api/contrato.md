# Contrato de la API · Demanda360

> Fuente: plan del MVP, sección 4. Cualquier cambio en este archivo necesita la aprobación del líder técnico (Rol 1) y de pantallas (Rol 4).
> **Forma exacta de cada respuesta:** los archivos de `frontend/static/mock/`. Si un mock y este documento no coinciden, se corrige uno de los dos por PR; el backend devuelve exactamente la forma del mock.

## Estado de implementación

| Ruta | Prioridad | Estado |
| --- | --- | --- |
| `GET /api/health` | P0 | Implementada (etapa 1) |
| `GET /api/auditoria` | P0 | Implementada (etapa 1) |
| Productos, conteos, ventas, movimientos, dashboard, rotación | P0 | Etapa 3 |
| Sugeridos y pedidos | P1 | Etapa 5 |

## Precisiones de la etapa 1 (no cambian el plan)

- **Estados de producto** (valor exacto en JSON): `SIN_CONTEO`, `AGOTADO`, `CRITICO`, `DATOS_INSUFICIENTES`, `BAJA_ROTACION`, `NORMAL`. Clase CSS: `etiqueta-` + estado en minúsculas con guiones (`etiqueta-baja-rotacion`).
- **`saldo: null`** significa «Sin conteo». Nunca se muestra como 0.
- **Errores 500** agregan `error.referencia`, igual a la cabecera `X-Request-ID`, para encontrar el detalle en el log. Nunca traen trazas.
- **405** responde `METODO_NO_PERMITIDO` con el mismo formato.
- **CSRF inválido o ausente** en un `POST /api/*`: `400 VALIDACION` con `campos: {"csrf": "invalido"}`.
- **Sesión y rol en pantallas:** `base.html` deja el rol en `<body data-rol="...">`. Los elementos con clase `solo-propietario` se ocultan al trabajador (solo comodidad visual: el backend igual responde 403).

## Decisiones abiertas (pendientes de aprobar)

1. **Cliente que regresa (`solicitud_previa_id`).** El plan dice «no se crea otra solicitud». Propuesta: sí se crea la fila de atención, enlazada con `solicitud_previa_id`, y la vista del KPI 2 la excluye del denominador. Ventaja: toda VENTA nace de una atención (trazabilidad completa) y la regla del KPI vive en un solo lugar. El esquema ya lo soporta.
2. **Proveedores de la demo.** En el Figma un solo proveedor tiene plazos de 3, 4 y 5 días, pero el plazo vive en el proveedor. Los datos simulados usan 4 proveedores ficticios (3, 4, 5 y 7 días) para conservar las columnas «Entrega (d)» del Figma.
3. **Fecha de corte de los KPI.** Ver la nota de la etapa 2 en el README.

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
    { "codigo": "KPI3", "nombre": "Baja rotación", "valor": 50.0, "unidad": "%", "numerador": 5, "denominador": 10, "nota": "1 referencia con datos insuficientes" }
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
