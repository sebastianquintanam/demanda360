# CSV para Power BI · Demanda360

> **Datos SIMULADOS** (1 al 30 de septiembre de 2026). No son datos de Pinturas By-plus. Todas las páginas del tablero llevan la marca «Datos simulados».

Estos archivos los genera `analytics/exportar_csv.sh` desde las vistas de `database/sql/02_vistas.sql`. **No se editan a mano.** Si una cifra no cuadra, se avisa al líder de desarrollo y se corrige la vista; después se vuelven a exportar.

## Cómo abrirlos

- **Power BI:** Obtener datos → Texto/CSV. Origen del archivo: *65001: Unicode (UTF-8)*. Delimitador: *Coma*.
- **Ojo con los decimales:** los archivos usan **punto** decimal (`27.3`). Si tu Windows está en español, Power BI puede leer `27.3` como `273`. Antes de importar, cambia la configuración regional de importación del archivo a *Inglés (Estados Unidos)*: Archivo → Opciones y configuración → Opciones → Archivo actual → Configuración regional. Comprobación rápida: el KPI 1 debe verse como 27,3 y no como 273.
- **Excel:** no abras el CSV con doble clic, porque se ve todo en una columna. Usa Datos → Obtener datos → Desde texto/CSV, con las mismas opciones.

## Archivos

| Archivo | Una fila por | Para qué página |
| --- | --- | --- |
| `kpi_resumen.csv` | KPI (5 filas) | 1. Resumen |
| `inventario_actual.csv` | referencia al 30 de septiembre (11) | 2. Disponibilidad y 4. Baja rotación |
| `ventas_diarias.csv` | día × referencia (30 × 11 = 330) | 3. Demanda |
| `solicitudes.csv` | atención a un cliente (89) | 3. Demanda (detalle) |
| `pedidos.csv` | pedido a proveedor (5) | 5. Pedidos y proveedores |

Todos traen `corte` (2026-09-30) y `origen_datos` (`SIMULADO`). Las fechas con hora están en hora de Bogotá. Las columnas de sí o no usan `SI` y `NO`.

### kpi_resumen.csv

`codigo`, `nombre`, `valor`, `unidad` (`%` u `horas`), `numerador`, `denominador`, `detalle`, `periodo_desde`, `periodo_hasta`, `mejor_si` (`menor` en los KPI 1 a 4, `mayor` en el 5). Ningún valor es una meta lograda: es la línea de base simulada.

### inventario_actual.csv

Estado de cada referencia **al corte**, no en vivo, para que cuadre con el KPI 1.
`saldo` vacío significa «Sin conteo», que no es lo mismo que 0. `estado` puede ser `AGOTADO`, `CRITICO`, `DATOS_INSUFICIENTES`, `BAJA_ROTACION`, `NORMAL` o `SIN_CONTEO`.
`dias_con_registro` cuenta los días desde el primer conteo hasta el corte; con menos de 30, la referencia tiene datos insuficientes.
`vendidas_30d`, `no_atendidas_30d`, `demanda_30d` (vendidas + no atendidas), `demanda_diaria` (demanda ÷ 30), `cobertura_dias` (saldo ÷ demanda diaria, sin decimales), `cobertura_menor_que_plazo` (`SI` si el saldo no alcanza para esperar al proveedor), `sugerido_14d` (cantidad sugerida para 14 días; vacío = cantidad manual).

### ventas_diarias.csv

`fecha`, `sku`, `nombre`, `categoria`, `vendidas`, `solicitadas`, `no_atendidas`, `atenciones`. Incluye los días sin movimiento (en 0) para que la línea de tendencia no salte días. Los domingos no hay ventas.

### solicitudes.csv

Lo que pidió el cliente (`cantidad_solicitada`) y lo que se le entregó (`cantidad_entregada`). `no_atendida` es la diferencia. No hay datos del cliente.
`es_regreso = SI` marca a un cliente que volvió por lo que le faltó: esa fila **no** cuenta en el KPI 2 (`cuenta_en_kpi2 = NO`). En los datos demo no hay ninguna.

### pedidos.csv

`cadena_id` agrupa un pedido y sus reintentos con otros proveedores (`numero_intento` 1, 2…). `horas_respuesta` es el tiempo entre envío y respuesta del proveedor; **no** es el plazo de entrega. `horas_esperando_al_corte` aplica a los enviados sin respuesta. `confirmado_primer_proveedor = SI` alimenta el KPI 5.

## Hoja de verificación (recalcular a mano en Excel)

| KPI | Archivo | Cálculo | Resultado esperado |
| --- | --- | --- | --- |
| 1. Referencias agotadas | inventario_actual | filas con `saldo` = 0 ÷ filas con `saldo` no vacío × 100 | 3 ÷ 11 = 27,3 % |
| 2. Demanda no atendida | solicitudes (`cuenta_en_kpi2` = SI) | suma de `no_atendida` ÷ suma de `cantidad_solicitada` × 100 | 12 ÷ 139 = 8,6 % |
| 3. Baja rotación | inventario_actual (`dias_con_registro` ≥ 30) | filas con `saldo` > 0 y `vendidas_30d` ≤ 2 ÷ esas filas × 100 | 5 ÷ 10 = 50 % |
| 4. Confirmación del proveedor | pedidos (`horas_respuesta` no vacío) | promedio de `horas_respuesta` | (3 + 6 + 5) ÷ 3 = 4,7 h |
| 5. Primer proveedor | pedidos (`estado` = CONFIRMADO) | filas con `confirmado_primer_proveedor` = SI ÷ esas filas × 100 | 2 ÷ 3 = 66,7 % |

Controles extra: la suma de `vendidas` en `ventas_diarias` es 127 y la de `no_atendidas` es 12. La suma de `sugerido_14d` es 54, y la laca alto brillo (`LAC-BP-01`) tiene 24.
