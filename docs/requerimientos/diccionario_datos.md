# Demanda360 — Diccionario de datos

**Entregable E7 · Rol 3, datos y Power BI**  
**Revisión del esquema:** 8 de noviembre de 2026  
**Corte de la demostración:** 30 de septiembre de 2026 · **Datos simulados**

Este diccionario describe las 11 tablas de PostgreSQL y los campos de las cinco exportaciones analíticas. Las definiciones se cotejaron con el [esquema](../../database/sql/01_schema.sql), las [vistas y funciones](../../database/sql/02_vistas.sql) y el [script de exportación](../../analytics/exportar_csv.sh). Las [fichas de KPI](kpi.md) explican el uso de los indicadores y la [comparación Excel–CSV](../../analytics/consultas/comparacion_kpi_excel_csv.md) registra los resultados del corte de demostración.

## Convenciones

- **PK** identifica una fila y **FK** señala la tabla y columna a la que hace referencia. Cada `id` de las tablas físicas es un `bigint` generado por PostgreSQL como identidad.
- **Admite NULL** indica si el esquema permite ausencia de valor. Las condiciones de negocio pueden volver obligatorio un campo en ciertos estados. Un `NULL` significa ausencia o inaplicabilidad según el campo. Un cero expresa una cantidad calculada o registrada.
- `timestamptz` representa un instante y la base opera en `America/Bogota`. Los CSV expresan fechas ISO y horas locales de Bogotá sin zona explícita. `date` representa un día de calendario.
- Las cantidades son enteros en la unidad propia de cada SKU. Un galón y un cuñete son referencias distintas. Los costos y precios usan `numeric(12,2)`, con dos posiciones decimales.

## Tablas de PostgreSQL

### `usuarios` · Una cuenta del sistema por fila

| Campo | Tipo SQL | Admite NULL | Significado y regla |
| --- | --- | --- | --- |
| `id` | `bigint` | No | PK de la cuenta. |
| `nombre` | `varchar(120)` | No | Nombre de la persona usuaria. |
| `usuario` | `varchar(50)` | No | Identificador de acceso único, en minúsculas y de al menos tres caracteres. |
| `password_hash` | `varchar(255)` | No | Hash de la contraseña. Campo reservado para autenticación. |
| `rol` | `varchar(20)` | No | `propietario` o `trabajador`. |
| `activo` | `boolean` | No | Estado de habilitación. Valor inicial `true`. |
| `creado_en` | `timestamptz` | No | Fecha y hora de creación. Por defecto `now()`. |

### `categorias` · Una categoría de productos por fila

| Campo | Tipo SQL | Admite NULL | Significado y regla |
| --- | --- | --- | --- |
| `id` | `bigint` | No | PK de la categoría. |
| `nombre` | `varchar(80)` | No | Nombre no vacío. Único al comparar en minúsculas y sin espacios de los extremos. |

### `proveedores` · Un proveedor por fila

| Campo | Tipo SQL | Admite NULL | Significado y regla |
| --- | --- | --- | --- |
| `id` | `bigint` | No | PK del proveedor. |
| `codigo` | `varchar(20)` | No | Código único en mayúsculas. |
| `nombre` | `varchar(120)` | No | Nombre comercial. |
| `plazo_entrega_dias` | `integer` | No | Plazo estimado de entrega en días, mayor que cero. Se compara con la cobertura. |
| `contacto` | `varchar(120)` | Sí | Dato de contacto opcional, de uso operativo. |
| `activo` | `boolean` | No | Estado de habilitación. Valor inicial `true`. |
| `creado_en` | `timestamptz` | No | Fecha y hora de alta. Por defecto `now()`. |

### `productos` · Una referencia por SKU

| Campo | Tipo SQL | Admite NULL | Significado y regla |
| --- | --- | --- | --- |
| `id` | `bigint` | No | PK del producto. |
| `sku` | `varchar(30)` | No | Código único de la referencia. Entre 3 y 30 caracteres, con letras mayúsculas, dígitos y guiones. Empieza con letra o dígito. |
| `nombre` | `varchar(150)` | No | Nombre de la referencia. Debe contener texto. |
| `categoria_id` | `bigint` | No | FK → `categorias.id`. |
| `proveedor_id` | `bigint` | No | FK → `proveedores.id`. Proveedor de referencia del catálogo. |
| `marca` | `varchar(80)` | Sí | Marca comercial. |
| `presentacion` | `varchar(60)` | No | Descripción de la presentación. |
| `unidad_medida` | `varchar(20)` | No | `unidad`, `galon`, `medio_galon`, `cuarto_galon`, `cunete`, `litro` o `kilogramo`. |
| `costo_compra` | `numeric(12,2)` | No | Costo de compra por unidad de la referencia, mayor o igual a cero. |
| `precio_venta` | `numeric(12,2)` | No | Precio de venta por unidad de la referencia, mayor o igual a cero. |
| `umbral_reposicion` | `integer` | No | Cantidad de alerta configurada, mayor o igual a cero. |
| `activo` | `boolean` | No | Estado de habilitación. Valor inicial `true`. |
| `creado_en` | `timestamptz` | No | Fecha y hora de alta. Por defecto `now()`. |

### `conteos_fisicos` · Un conteo físico de una referencia por fila

| Campo | Tipo SQL | Admite NULL | Significado y regla |
| --- | --- | --- | --- |
| `id` | `bigint` | No | PK del conteo. |
| `producto_id` | `bigint` | No | FK → `productos.id`. |
| `cantidad_contada` | `integer` | No | Existencias observadas en el conteo, mayores o iguales a cero. |
| `fecha_hora` | `timestamptz` | No | Instante del conteo. Por defecto `now()`. |
| `usuario_id` | `bigint` | No | FK → `usuarios.id`. Cuenta que registra el conteo. |
| `observaciones` | `varchar(300)` | Sí | Nota opcional sobre el conteo. |
| `origen_ref` | `varchar(64)` | Sí | Folio de origen. Debe ser único cuando se informa. |

### `movimientos` · Un cambio de inventario por fila

| Campo | Tipo SQL | Admite NULL | Significado y regla |
| --- | --- | --- | --- |
| `id` | `bigint` | No | PK del movimiento. |
| `producto_id` | `bigint` | No | FK → `productos.id`. |
| `tipo` | `varchar(10)` | No | `VENTA`, `ENTRADA` o `AJUSTE`. |
| `cantidad` | `integer` | No | Entero positivo en venta o entrada. Un ajuste admite signo positivo o negativo y debe ser distinto de cero. |
| `fecha_hora` | `timestamptz` | No | Instante del movimiento. Por defecto `now()`. |
| `usuario_id` | `bigint` | No | FK → `usuarios.id`. Cuenta que registra el movimiento. |
| `origen_ref` | `varchar(64)` | No | Folio único para identificar el origen y evitar registros duplicados. Admite folios de contingencia. |
| `justificacion` | `varchar(500)` | Sí | Obligatoria para `AJUSTE`, con al menos diez caracteres una vez recortados los espacios extremos. |

### `solicitudes_clientes` · Una atención para una referencia por fila

| Campo | Tipo SQL | Admite NULL | Significado y regla |
| --- | --- | --- | --- |
| `id` | `bigint` | No | PK de la atención. |
| `producto_id` | `bigint` | No | FK → `productos.id`. |
| `cantidad_solicitada` | `integer` | No | Unidades solicitadas. Entero mayor que cero. |
| `cantidad_entregada` | `integer` | No | Unidades entregadas, entre cero y la cantidad solicitada. |
| `fecha_hora` | `timestamptz` | No | Instante de atención. Por defecto `now()`. |
| `usuario_id` | `bigint` | No | FK → `usuarios.id`. Cuenta que registra la atención. |
| `movimiento_id` | `bigint` | Sí | FK → `movimientos.id`. Enlace único a la venta. Se informa si se entregó alguna unidad y queda vacío si se entregaron cero. |
| `solicitud_previa_id` | `bigint` | Sí | FK → `solicitudes_clientes.id`. Atención original si hubo regreso por un faltante. No admite referencia a la misma fila. |
| `origen_ref` | `varchar(64)` | No | Folio único de la atención. |

### `auditoria` · Un evento de auditoría por fila

| Campo | Tipo SQL | Admite NULL | Significado y regla |
| --- | --- | --- | --- |
| `id` | `bigint` | No | PK del evento. |
| `usuario_id` | `bigint` | Sí | FK → `usuarios.id`. Cuenta asociada, cuando está disponible. |
| `accion` | `varchar(50)` | No | Código de la acción. |
| `entidad` | `varchar(50)` | No | Tipo de objeto sobre el que ocurrió la acción. |
| `entidad_id` | `bigint` | Sí | Identificador del objeto afectado. Se interpreta junto con `entidad`. |
| `fecha_hora` | `timestamptz` | No | Instante del evento. Por defecto `now()`. |
| `detalle` | `jsonb` | No | Contexto mínimo del evento. Valor inicial `{}`. Se excluyen contraseñas y credenciales. |

### `alertas_enviadas` · Un evento de alerta por fila

| Campo | Tipo SQL | Admite NULL | Significado y regla |
| --- | --- | --- | --- |
| `id` | `bigint` | No | PK interna de la alerta. |
| `evento_id` | `uuid` | No | Identificador único del evento para reconocer reintentos de la misma alerta. |
| `producto_id` | `bigint` | No | FK → `productos.id`. |
| `movimiento_id` | `bigint` | Sí | FK → `movimientos.id`. Movimiento relacionado, cuando se informa. |
| `saldo` | `integer` | No | Saldo registrado en el evento de alerta. Es una observación del evento. |
| `umbral` | `integer` | No | Umbral registrado en el evento de alerta. |
| `estado` | `varchar(10)` | No | `PENDIENTE`, `ENVIADA` o `FALLIDA`. Valor inicial `PENDIENTE`. |
| `intentos` | `integer` | No | Intentos de envío, con mínimo cero. Valor inicial `0`. |
| `ultimo_error` | `varchar(200)` | Sí | Último error de envío registrado. |
| `creado_en` | `timestamptz` | No | Instante de creación del evento. Por defecto `now()`. |
| `enviado_en` | `timestamptz` | Sí | Instante de envío exitoso. Se informa exactamente cuando el estado es `ENVIADA`. |

### `pedidos` · Un intento de pedido a un proveedor por fila

| Campo | Tipo SQL | Admite NULL | Significado y regla |
| --- | --- | --- | --- |
| `id` | `bigint` | No | PK del intento. |
| `proveedor_id` | `bigint` | No | FK → `proveedores.id`. Proveedor de este intento. |
| `estado` | `varchar(12)` | No | `BORRADOR`, `APROBADO`, `ENVIADO`, `CONFIRMADO` o `CANCELADO`. Valor inicial `BORRADOR`. |
| `numero_intento` | `integer` | No | Ordinal dentro de la cadena. Valor inicial y mínimo `1`. |
| `pedido_anterior_id` | `bigint` | Sí | FK → `pedidos.id`. Vacío solo en el primer intento. Cada pedido puede ser antecedente de un solo sucesor. |
| `creado_por` | `bigint` | No | FK → `usuarios.id`. Cuenta que creó el intento. |
| `aprobado_por` | `bigint` | Sí | FK → `usuarios.id`. Obligatoria en `APROBADO`, `ENVIADO` y `CONFIRMADO`. |
| `fecha_creacion` | `timestamptz` | No | Instante de creación. Por defecto `now()`. |
| `fecha_aprobacion` | `timestamptz` | Sí | Instante de aprobación. Obligatorio en `APROBADO`, `ENVIADO` y `CONFIRMADO`. |
| `fecha_envio` | `timestamptz` | Sí | Instante de envío. Obligatorio en `ENVIADO` y `CONFIRMADO`. |
| `fecha_respuesta` | `timestamptz` | Sí | Instante de respuesta. Obligatorio en `CONFIRMADO`. |
| `fecha_entrega_estimada` | `date` | Sí | Día previsto de llegada de la mercancía. |
| `motivo_cancelacion` | `varchar(300)` | Sí | Motivo obligatorio y no vacío en `CANCELADO`. |

La base compara la creación con la aprobación, la aprobación con el envío y el envío con la respuesta cuando están informadas las fechas correspondientes. La [aplicación](../../backend/app/routes/pedidos.py) permite crear borradores a ambos roles y reserva la aprobación, envío, confirmación y cancelación al propietario. Un reintento con otro proveedor se enlaza al pedido cancelado, incrementa el ordinal y nace aprobado por el propietario. La entrada de mercancía se registra aparte cuando llega.

### `pedido_detalles` · Una referencia incluida en un intento por fila

| Campo | Tipo SQL | Admite NULL | Significado y regla |
| --- | --- | --- | --- |
| `id` | `bigint` | No | PK de la línea. |
| `pedido_id` | `bigint` | No | FK → `pedidos.id`. El par `pedido_id` y `producto_id` es único. |
| `producto_id` | `bigint` | No | FK → `productos.id`. Referencia solicitada. |
| `cantidad_sugerida` | `integer` | Sí | Cantidad sugerida por el cálculo al preparar el pedido. Si existe, es mayor o igual a cero. Cuando falta un cálculo se permite indicar la cantidad manualmente. |
| `cantidad_solicitada` | `integer` | No | Cantidad incluida en el pedido. Entero mayor que cero. |

## Relaciones y reglas de cálculo

- Cada producto pertenece a una categoría y tiene un proveedor de referencia. Un producto puede tener muchos conteos, movimientos, atenciones, alertas y líneas de pedido. Una atención puede enlazar como máximo una venta y un antecedente. Un pedido tiene un proveedor, una cuenta creadora y una cuenta aprobadora cuando corresponda. `pedido_detalles` conecta pedidos y productos.
- `conteos_fisicos`, `movimientos`, `solicitudes_clientes` y `auditoria` son de solo inserción. La base bloquea `UPDATE` y `DELETE` con disparadores. Las correcciones de inventario se registran como ajustes o nuevos conteos.
- **Saldo.** `fn_saldos` toma el último conteo anterior al límite, suma entradas y ajustes con signo, y resta ventas posteriores al conteo. Un movimiento con la misma marca de tiempo que el conteo se considera incluido. Ante un empate de conteos se elige el mayor `id`. Sin conteo, el saldo es `NULL`. El saldo de una alerta es el que quedó registrado en ese evento.
- **Corte.** La ventana incluye el día de corte y los 29 días anteriores, desde medianoche hasta el inicio del día siguiente al corte, con límite superior exclusivo en Bogotá. `fn_corte()` toma `demanda360.corte` y usa `2026-09-30` como valor predeterminado. `fn_origen_datos()` usa `SIMULADO` por defecto.
- **Demanda y ventas.** `demanda_30d` suma las unidades solicitadas en atenciones originales. Una atención de regreso queda enlazada a la original y se excluye de la demanda solicitada y no atendida del KPI 2. Las unidades entregadas en un regreso sí cuentan en ventas. Por eso, sumar ventas y faltantes coincide con la demanda en esta demo, pero puede diferir en otro corte.
- **Estado de inventario.** Se aplica el primer caso que corresponda. El orden es `SIN_CONTEO` si falta saldo, `AGOTADO` si el saldo es menor o igual a cero, `CRITICO` si el saldo positivo es menor o igual al umbral, `DATOS_INSUFICIENTES` con menos de 30 días de registro, `BAJA_ROTACION` con hasta dos unidades vendidas, y `NORMAL` en los demás casos. El KPI 3 evalúa saldo positivo, días de registro y ventas. El recuento de la etiqueta `BAJA_ROTACION` puede diferir del KPI 3 porque `CRITICO` tiene precedencia en el estado.
- **Sugerido.** `fn_sugeridos` aplica `máx(0, techo(demanda_30d × días objetivo / 30 − saldo))` con la demanda sin redondear. El CSV usa 14 días. Sin conteo o con menos de 30 días de registro, deja la cantidad vacía para decisión manual.

## Vistas y exportaciones

| Vista SQL | Archivo de demostración | Una fila por | Filas verificadas | Uso |
| --- | --- | --- | --- | --- |
| `vw_inventario_actual` | `inventario_actual.csv` | Producto activo creado hasta el corte | 11 | Disponibilidad y detalle de Baja rotación. |
| `vw_ventas_diarias` | `ventas_diarias.csv` | Fecha y producto | 330 | Tendencia y comparación por SKU en Demanda. |
| `vw_solicitudes` | `solicitudes.csv` | Atención del período | 89 | Verificación del KPI 2 desde las atenciones. |
| `vw_kpi_resumen` | `kpi_resumen.csv` | KPI y corte | 5 | Tarjetas del Resumen y de las páginas temáticas. |
| `vw_pedidos` | `pedidos.csv` | Intento de pedido creado hasta el corte | 5 | Estados, respuestas y reintentos por proveedor. |

Los [CSV de demostración](../../analytics/datos_demo/README.md) usan UTF-8 con BOM, coma como separador y punto decimal. Los cinco incluyen `corte` y `origen_datos`. Los encabezados de las tablas siguientes siguen el orden de los archivos. Los tipos describen el dato exportado, aunque el CSV lo transporte como texto. En el `.pbix` de septiembre, `baja_rotacion_detalle` deriva de `inventario_actual` y conserva los estados `BAJA_ROTACION` y `DATOS_INSUFICIENTES`. `solicitudes.csv` se usó para el cotejo y el tablero de Demanda se alimenta de `ventas_diarias.csv` y `kpi_resumen.csv`.

Las vistas auxiliares `vw_saldos` y `vw_estado_productos` muestran saldo actual. La segunda usa métricas del período de corte para la clasificación. `vw_sugeridos` ofrece la reposición al corte con 14 días objetivo y la versión de la regla. `vw_kpi_agotadas`, `vw_kpi_demanda`, `vw_kpi_rotacion`, `vw_kpi_respuesta` y `vw_kpi_primer_proveedor` filtran una fila de `vw_kpi_resumen` cada una. `vw_pedidos` selecciona los intentos por fecha de creación y expone el estado y las fechas que estén guardados al exportar.

### `inventario_actual.csv`

| Campo | Tipo | Origen e interpretación |
| --- | --- | --- |
| `corte` | Fecha | Último día de la ventana del informe. |
| `producto_id` | Entero | `productos.id`. |
| `sku` | Texto | Código de la referencia. |
| `nombre` | Texto | Nombre del producto. |
| `categoria` | Texto | `categorias.nombre`. |
| `proveedor` | Texto | Nombre del proveedor del catálogo. |
| `plazo_entrega_dias` | Entero | Días de entrega del proveedor. |
| `presentacion` | Texto | Presentación de la referencia. |
| `unidad_medida` | Texto | Unidad de la referencia. |
| `umbral_reposicion` | Entero | Umbral del catálogo en unidades. |
| `saldo` | Entero | Saldo al corte. Vacío si falta conteo. |
| `estado` | Texto | Estado de inventario según la precedencia anterior. |
| `dias_con_registro` | Entero | Días calendario desde el primer conteo hasta el corte, ambos incluidos. Vacío sin conteo. |
| `vendidas_30d` | Entero | Unidades vendidas según movimientos de venta del período. |
| `no_atendidas_30d` | Entero | Faltantes de atenciones originales del período. |
| `demanda_30d` | Entero | Total solicitado en atenciones originales del período. |
| `demanda_diaria` | Decimal | Demanda dividida entre 30 y presentada con dos decimales. Vacía con menos de 30 días de registro o sin conteo. |
| `cobertura_dias` | Entero | Piso de saldo no negativo dividido por la demanda diaria sin redondear. Vacío si falta conteo, hay menos de 30 días de registro o la demanda es cero. |
| `cobertura_menor_que_plazo` | `SI`/`NO` | `SI` cuando existe cobertura y es menor que el plazo de entrega. También devuelve `NO` cuando falta la cobertura, por lo que se debe leer con `cobertura_dias`. |
| `sugerido_14d` | Entero | Reposición sugerida para 14 días. Vacío si se requiere cantidad manual. |
| `origen_datos` | Texto | `SIMULADO` en la demostración. |

### `ventas_diarias.csv`

| Campo | Tipo | Origen e interpretación |
| --- | --- | --- |
| `fecha` | Fecha | Día del período en Bogotá. Incluye los días sin movimiento. |
| `producto_id` | Entero | `productos.id`. Junto con `fecha` identifica la fila dentro de un corte. |
| `sku` | Texto | Código de la referencia. |
| `nombre` | Texto | Nombre del producto. |
| `categoria` | Texto | Nombre de la categoría. |
| `vendidas` | Entero | Unidades en movimientos `VENTA` del día. Incluye las entregas en regresos. |
| `solicitadas` | Entero | Unidades solicitadas en atenciones originales del día. |
| `no_atendidas` | Entero | Solicitadas menos entregadas de las atenciones originales del día. |
| `atenciones` | Entero | Número de atenciones originales del día. |
| `corte` | Fecha | Último día de la ventana del informe. |
| `origen_datos` | Texto | `SIMULADO` en la demostración. |

### `solicitudes.csv`

| Campo | Tipo | Origen e interpretación |
| --- | --- | --- |
| `solicitud_id` | Entero | `solicitudes_clientes.id`. |
| `fecha_hora` | Fecha y hora | Momento de la atención, en hora de Bogotá. |
| `fecha` | Fecha | Día local de la atención. |
| `producto_id` | Entero | `productos.id`. |
| `sku` | Texto | Código de la referencia. |
| `nombre` | Texto | Nombre del producto. |
| `categoria` | Texto | Nombre de la categoría. |
| `cantidad_solicitada` | Entero | Unidades solicitadas en la atención. |
| `cantidad_entregada` | Entero | Unidades entregadas en la atención. |
| `no_atendida` | Entero | Diferencia entre lo solicitado y lo entregado en esa fila. |
| `es_regreso` | `SI`/`NO` | `SI` si existe una atención original enlazada. |
| `solicitud_previa_id` | Entero | Identificador de la atención original. Vacío para atenciones originales. |
| `cuenta_en_kpi2` | `SI`/`NO` | `SI` para atenciones originales. Filtrar por este valor al recalcular el KPI 2. |
| `registrado_por_rol` | Texto | Rol de la cuenta que registró la atención. |
| `corte` | Fecha | Último día de la ventana del informe. |
| `origen_datos` | Texto | `SIMULADO` en la demostración. |

### `kpi_resumen.csv`

| Campo | Tipo | Origen e interpretación |
| --- | --- | --- |
| `corte` | Fecha | Corte calculado. |
| `periodo_desde` | Fecha | Primer día de la ventana, `corte − 29 días`. |
| `periodo_hasta` | Fecha | Último día de la ventana, igual al corte. |
| `codigo` | Texto | `KPI1` a `KPI5`. Junto con `corte` identifica la fila. |
| `nombre` | Texto | Nombre de presentación del KPI. |
| `valor` | Decimal | Resultado a un decimal. Porcentaje en escala 0–100 u horas según `unidad`. Vacío si no hay denominador. |
| `unidad` | Texto | `%` en KPI 1, 2, 3 y 5. `horas` en KPI 4. |
| `numerador` | Decimal | Referencias, unidades, horas acumuladas o intentos, según el KPI. |
| `denominador` | Entero | Base del cálculo. Referencias, unidades o intentos según el KPI. |
| `detalle` | Texto | Explicación de la base o exclusiones del cálculo. |
| `mejor_si` | Texto | `menor` en KPI 1 a 4 y `mayor` en KPI 5. |
| `origen_datos` | Texto | `SIMULADO` en la demostración. |

### `pedidos.csv`

| Campo | Tipo | Origen e interpretación |
| --- | --- | --- |
| `pedido_id` | Entero | `pedidos.id`. Identifica un intento. |
| `cadena_id` | Entero | Identificador del primer pedido de la cadena, calculado siguiendo los enlaces al intento anterior. |
| `numero_intento` | Entero | Ordinal del intento dentro de la cadena. |
| `pedido_anterior_id` | Entero | Intento anterior. Vacío en el primero. |
| `proveedor` | Texto | Nombre del proveedor de este intento. |
| `plazo_entrega_dias` | Entero | Plazo estimado de entrega en días. |
| `estado` | Texto | Estado guardado del intento. |
| `fecha_creacion` | Fecha y hora | Instante de creación, en hora local. |
| `fecha_aprobacion` | Fecha y hora | Instante de aprobación. Vacío si no se registró. |
| `fecha_envio` | Fecha y hora | Instante de envío. Vacío si no se registró. |
| `fecha_respuesta` | Fecha y hora | Instante de respuesta. Vacío si no se registró. |
| `fecha_entrega_estimada` | Fecha | Día previsto de llegada, si se informó. |
| `horas_respuesta` | Decimal | Horas desde el envío hasta la respuesta, redondeadas a un decimal. Vacío si falta una de las dos fechas. |
| `horas_esperando_al_corte` | Decimal | Horas entre el envío y el límite exclusivo del corte. Aplica a un intento en `ENVIADO` sin respuesta. |
| `confirmado_primer_proveedor` | `SI`/`NO` | `SI` para un intento confirmado con ordinal 1. El KPI 5 además filtra por fecha de respuesta. |
| `motivo_cancelacion` | Texto | Motivo registrado para el intento cancelado, cuando existe. |
| `referencias` | Entero | Número de líneas de producto del intento. Cero si no hay detalles. |
| `unidades_solicitadas` | Entero | Suma de unidades incluidas en el intento. Cero si no hay detalles. |
| `unidades_sugeridas` | Entero | Suma de sugeridos informados. Vacío cuando todos faltan o no hay detalles. |
| `skus` | Texto | Lista de SKU del intento, ordenada y separada por comas. Vacía si no hay detalles. |
| `corte` | Fecha | Último día de la ventana del informe. |
| `origen_datos` | Texto | `SIMULADO` en la demostración. |

## Trazabilidad y controles del corte de demostración

| KPI | Regla aplicada en `fn_kpi_resumen` | Verificación de septiembre de 2026 |
| --- | --- | --- |
| KPI 1 · Agotadas | Referencias activas con saldo ≤ 0 sobre activas con saldo conocido al corte. | 3 / 11 = **27,3 %**. |
| KPI 2 · Demanda no atendida | Unidades faltantes sobre solicitadas en atenciones originales del período, para productos activos. | 12 / 139 = **8,6 %**. Se registraron 127 unidades vendidas. |
| KPI 3 · Baja rotación | Activas con saldo positivo, al menos 30 días de registro y hasta dos vendidas sobre activas con conteo y al menos 30 días de registro. | 5 / 10 = **50,0 %**. La laca transparente tiene 3 días de registro y queda fuera del denominador. |
| KPI 4 · Confirmación | Promedio de horas de los intentos enviados durante el período con respuesta anterior al límite del corte. Los envíos sin respuesta al corte se cuentan aparte. | (3 + 6 + 5) / 3 = **4,7 h**. Un intento está cancelado sin respuesta y otro sigue enviado sin respuesta. |
| KPI 5 · Primer proveedor | Intentos confirmados con ordinal 1 sobre los confirmados cuya respuesta ocurrió en el período. La aplicación enlaza cada reintento desde un pedido cancelado. | 2 / 3 = **66,7 %**. Los tres confirmados pertenecen a tres cadenas distintas. |

El inventario al corte contiene 11 referencias y suma 54 unidades sugeridas calculadas. La cantidad manual de la laca transparente se mantiene vacía. La tabla de ventas diarias contiene 30 días por cada una de las 11 referencias, incluidos los días sin movimiento.

## Uso y minimización de datos

Las atenciones guardan cantidades y enlaces operativos. El esquema no tiene campos de identidad o contacto del cliente. Los CSV exponen el rol de registro en lugar del nombre de la cuenta y omiten hashes, contactos de proveedores y detalles de auditoría. Los proveedores y las cifras del corte son ficticios.

Para reproducir el tablero en otro equipo, se debe usar el mismo corte en las cinco exportaciones y actualizar las rutas de origen de los CSV en Power BI. Los gráficos y notas de la demostración se interpretan con el período visible en el informe. Para acreditar un movimiento posterior se requiere una exportación del corte que lo incluya.
