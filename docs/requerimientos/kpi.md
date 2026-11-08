# Demanda360 — Fichas de los cinco KPI

Proyecto integrador de Fundamentos de Sistemas de Información · Universidad EAN  
Caso: Pinturas By-plus · Responsable de elaboración: rol 3 · Fecha: 8 de noviembre de 2026

## Alcance y estado

Estas fichas desarrollan los cinco indicadores definidos en el plan del MVP. La auditoría de Sebastián del 8 de noviembre de 2026 informa que las vistas de KPI y los CSV están implementados. El cotejo del rol 3 confirma que los cinco resultados guardados en Excel coinciden con los CSV de septiembre al mostrarlos con un decimal. La ejecución de las consultas SQL y de las pruebas del backend no forma parte de este cotejo.

El historial de septiembre de 2026 es **SIMULADO**. Los valores de demostración no constituyen una línea base real ni prueban reducción de agotamientos, ahorros o mejoras en el negocio. Los datos reales se conservarán separados de los simulados.

## Reglas comunes de presentación

- Mostrar nombre, período, fecha de corte o de exportación, valor y origen de los datos. En porcentajes, incluir numerador y denominador; en promedios, indicar cuántos pedidos se incluyeron.
- Utilizar la hora de Bogotá. Las existencias se evalúan al corte; las ventas y solicitudes corresponden al período indicado.
- Un cero verificado es diferente de un dato faltante. Si el denominador es cero, mostrar «Sin datos para calcular», nunca 0 % ni 0 horas.
- Mantener la precisión del cálculo y redondear únicamente la presentación. Mostrar porcentajes con un decimal.
- Las metas de los KPI 1 a 3 son provisionales y relativas a una futura línea base real. Una reducción del 20 % relativo se calcula como línea base × 0,80; no equivale a restar 20 puntos porcentuales.
- Los propietarios validan las reglas y las metas. La aplicación y Power BI deben usar la misma definición y el mismo corte; los CSV requieren exportación y actualización para reflejar cambios.

## KPI 1. Porcentaje de referencias agotadas

| Campo | Definición |
| --- | --- |
| 1. Nombre | Porcentaje de referencias agotadas. |
| 2. Objetivo | Mejorar la disponibilidad e identificar las referencias que requieren revisión de reposición. |
| 3. Fórmula | (Referencias con saldo verificado igual a cero al corte / referencias monitoreadas con conteo verificado al corte) × 100. |
| 4. Unidad | Porcentaje (%). |
| 5. Fuente | Catálogo `productos`, `conteos_fisicos` y `movimientos`. El saldo se obtiene del último conteo y los movimientos posteriores hasta el corte. Vista de referencia: `vw_kpi_agotadas`. |
| 6. Frecuencia | Mensual, con fecha de corte explícita al cierre del período. |
| 7. Meta | Reducir un 20 % relativo frente a la primera línea base real validada. Meta provisional; valor inicial real pendiente de medición. |
| 8. Responsable | Propietarios. El personal registra conteos y movimientos; el rol 3 verifica el cálculo durante la demostración. |
| 9. Interpretación | Un valor menor indica una menor proporción de referencias agotadas en el corte. No informa cuántos días estuvieron agotadas ni cuánto dinero se dejó de vender. |
| 10. Calidad del dato | Contar cada referencia una sola vez. Excluir del numerador y del denominador los productos sin conteo; mostrarlos como «Sin conteo». No utilizar movimientos posteriores al corte. |

**Referencia simulada de septiembre de 2026:** 3 / 11 × 100 = **27,3 %**.

## KPI 2. Porcentaje de demanda no atendida inmediatamente

| Campo | Definición |
| --- | --- |
| 1. Nombre | Porcentaje de demanda no atendida inmediatamente. |
| 2. Objetivo | Atender una mayor proporción de las unidades solicitadas por los clientes en el momento de la compra. |
| 3. Fórmula | [Σ (cantidad solicitada − cantidad entregada en la atención inicial) / Σ cantidad solicitada] × 100. Las sumas usan la misma población de solicitudes del período. |
| 4. Unidad | Porcentaje (% de unidades solicitadas). |
| 5. Fuente | `solicitudes_clientes`: `cantidad_solicitada`, `cantidad_entregada`, `fecha_hora`, `solicitud_previa_id` y `origen_ref`. Vista de referencia: `vw_kpi_demanda`. |
| 6. Frecuencia | Mensual, según la fecha de la atención inicial. |
| 7. Meta | Reducir un 20 % relativo frente a la primera línea base real validada. Meta provisional; valor inicial real pendiente de medición. |
| 8. Responsable | Propietarios, con registro a cargo del personal de atención. El rol 3 verifica las cifras de la demostración. |
| 9. Interpretación | Un valor menor representa una mayor capacidad de atención inmediata. El indicador mide unidades, no clientes ni dinero perdido. |
| 10. Calidad del dato | Registrar una vez cada atención inicial, incluso si no se entrega ninguna unidad. Exigir solicitada > 0 y 0 ≤ entregada ≤ solicitada. Evitar duplicados con `origen_ref`. Una atención posterior vinculada por `solicitud_previa_id` no suma nueva demanda ni borra la falta de atención inmediata de la solicitud original. |

**Referencia simulada de septiembre de 2026:** 127 unidades vendidas y 12 no atendidas; 139 solicitadas. Resultado: 12 / 139 × 100 = **8,6 %**.

## KPI 3. Porcentaje de referencias de baja rotación

| Campo | Definición |
| --- | --- |
| 1. Nombre | Porcentaje de referencias de baja rotación. |
| 2. Objetivo | Identificar mercancía con poco movimiento para revisar las decisiones de abastecimiento. |
| 3. Fórmula | (Referencias con saldo > 0, entre 0 y 2 unidades vendidas y 30 días completos de registros / referencias monitoreadas con conteo verificado y 30 días completos de registros) × 100. |
| 4. Unidad | Porcentaje (%). |
| 5. Fuente | `productos`, `conteos_fisicos` y ventas de `movimientos` en la ventana de análisis. Vista de referencia: `vw_kpi_rotacion`. |
| 6. Frecuencia | Mensual, con ventana de 30 días completos y corte explícito. |
| 7. Meta | Reducir un 10 % relativo frente a la primera línea base real validada. Meta provisional; el criterio de 0 a 2 unidades debe validarse por familia de productos. |
| 8. Responsable | Propietarios. El rol 3 documenta y verifica el cálculo de demostración. |
| 9. Interpretación | Un valor menor puede indicar una menor proporción de referencias con poco movimiento. Debe interpretarse junto con disponibilidad y demanda no atendida: un agotamiento no demuestra baja demanda. No estima por sí solo el valor del capital inmovilizado. |
| 10. Calidad del dato | Excluir las referencias sin conteo o sin 30 días completos tanto del numerador como del denominador. Mostrar «Datos insuficientes» para registros incompletos. Las referencias agotadas no entran en el numerador porque se exige saldo positivo; pueden permanecer en el denominador si cumplen los requisitos. |

**Referencia simulada de septiembre de 2026:** 5 / 10 × 100 = **50,0 %**. La laca transparente se excluye porque solo tiene 3 días de registro.

## KPI 4. Tiempo de confirmación del proveedor

| Campo | Definición |
| --- | --- |
| 1. Nombre | Tiempo de confirmación del proveedor. |
| 2. Objetivo | Medir la espera entre enviar una solicitud y registrar la respuesta del proveedor, para dar seguimiento al proceso. |
| 3. Fórmula | Promedio de [(fecha_respuesta − fecha_envio) expresado en horas], para los pedidos incluidos en el período con ambas fechas válidas. |
| 4. Unidad | Horas por pedido con respuesta registrada. |
| 5. Fuente | `pedidos`: `fecha_envio` y `fecha_respuesta`; `proveedores` para identificar el proveedor. Vista de referencia: `vw_kpi_respuesta`; exportación: `pedidos.csv` y `kpi_resumen.csv`. |
| 6. Frecuencia | Mensual, con período y corte explícitos. La demostración corresponde al 1 al 30 de septiembre de 2026. |
| 7. Meta | Pendiente de establecer después de obtener una línea base real. No hay un valor objetivo confirmado. |
| 8. Responsable | Propietarios, con registro de envío y respuesta a cargo de quien gestione el pedido. |
| 9. Interpretación | Un tiempo menor indica una respuesta más rápida en los casos observados. No equivale al plazo de entrega de mercancía de 2 a 5 días. Debe mostrarse junto con el número de pedidos pendientes de respuesta. |
| 10. Calidad del dato | Excluir del promedio los pedidos sin ambas fechas y contarlos aparte. Exigir respuesta ≥ envío y zonas horarias coherentes. Mostrar el número de observaciones. Verificar que el criterio de respuesta y el filtro del período coincidan con la vista exportada. Separar los pedidos actualmente pendientes de los cancelados que tampoco tuvieron respuesta. |

**Resultado simulado verificado:** los tres pedidos con respuesta registran 3, 6 y 5 horas. El promedio es (3 + 6 + 5) / 3 = 4,6667 horas, presentado como **4,7 h**. Excel y `kpi_resumen.csv` coinciden a un decimal.

Hay dos intentos con fecha de envío y sin fecha de respuesta: el pedido 2 está **CANCELADO** y el pedido 5 está **ENVIADO**. Los dos se excluyen del promedio; únicamente el segundo sigue pendiente de respuesta. No presentar ambos como pedidos actualmente pendientes.

## KPI 5. Porcentaje de pedidos confirmados con el primer proveedor

| Campo | Definición |
| --- | --- |
| 1. Nombre | Porcentaje de pedidos confirmados con el primer proveedor. |
| 2. Objetivo | Conocer qué proporción de las necesidades de abastecimiento confirmadas se resuelve sin acudir a un proveedor alternativo. |
| 3. Fórmula | (Cadenas de pedidos confirmadas en el intento 1 / cadenas de pedidos confirmadas en el período) × 100. Cada cadena se cuenta una sola vez. |
| 4. Unidad | Porcentaje (% de cadenas confirmadas). |
| 5. Fuente | `pedidos`: `estado`, `numero_intento`, `pedido_anterior_id` y fechas de la gestión. Vista de referencia: `vw_kpi_primer_proveedor`; el CSV incluye `cadena_id` y `confirmado_primer_proveedor` para el cotejo. |
| 6. Frecuencia | Mensual, con período de confirmación explícito y consistente en numerador y denominador. |
| 7. Meta | Pendiente de establecer después de obtener una línea base real. No hay un valor objetivo confirmado. |
| 8. Responsable | Propietarios, con registro a cargo de quien gestione y confirme el pedido. |
| 9. Interpretación | Un valor mayor indica que más cadenas confirmadas se resolvieron en el primer intento. Mide el proceso de abastecimiento y no constituye una puntuación ni una clasificación de proveedores. |
| 10. Calidad del dato | Reconstruir cada cadena mediante `pedido_anterior_id` y verificar la secuencia de intentos. No contar intentos como pedidos independientes. Una cadena confirmada tras un reintento entra solo en el denominador. Un pedido cancelado sin confirmación no entra. Los pedidos pendientes se presentan aparte. |

**Resultado simulado verificado:** existen tres cadenas confirmadas; dos se resolvieron en el intento 1 y una en el intento 2. Resultado: 2 / 3 × 100 = 66,6667 %, presentado como **66,7 %**. Excel y `kpi_resumen.csv` coinciden a un decimal. El pedido cancelado y el que sigue enviado no aumentan el denominador de confirmados.

## Comprobación y evidencias del rol 3

| Indicador | Base de cálculo | Excel guardado | CSV | Cotejo a un decimal |
| --- | --- | --- | --- | --- |
| KPI 1 | 3 / 11 × 100 | 27,3 % | 27,3 % | Coincide. |
| KPI 2 | 12 / 139 × 100 | 8,6 % | 8,6 % | Coincide. |
| KPI 3 | 5 / 10 × 100; laca transparente excluida | 50,0 % | 50,0 % | Coincide. |
| KPI 4 | 14 horas / 3 respuestas | 4,7 h | 4,7 h | Coincide. |
| KPI 5 | 2 / 3 × 100 | 66,7 % | 66,7 % | Coincide. |

El cotejo utiliza los valores guardados en `analytics/consultas/verificacion_kpi.xlsx`, hoja `Datos_simulados.`, celdas D16:D20, frente a `analytics/datos_demo/kpi_resumen.csv`. Los cálculos del Excel conservan su precisión; la comparación se hace con la presentación a un decimal del CSV. El registro detallado está preparado para `analytics/consultas/comparacion_kpi_excel_csv.md`.

Las cinco tarjetas se han comprobado visualmente en el informe del rol 3. Quedan pendientes completar las páginas de Power BI, guardar las capturas en `docs/evidencias/` y documentar el flujo de una operación de demostración hasta su exportación y actualización en Power BI.

La reposición sugerida de **54 unidades** es una comprobación adicional del ejemplo, no un sexto KPI. Se obtiene con una cobertura de 14 días, usando `máx(0, techo((vendidas + no atendidas) / 30 × 14 − saldo))` para las referencias con datos suficientes. La cantidad manual de la laca transparente no forma parte de ese total.

## Distribución de las cinco páginas de Power BI

Se conserva la estructura temática de la sección 6 del plan, confirmada por el equipo el 8 de noviembre. Todas las páginas muestran **DATOS SIMULADOS** y el corte de los archivos importados.

| Página | Contenido e indicadores | CSV de referencia |
| --- | --- | --- |
| Resumen | Las cinco tarjetas, período y bases de cálculo. | `kpi_resumen.csv`. |
| Disponibilidad | Existencias, agotados, críticos y KPI 1. | `inventario_actual.csv` y `kpi_resumen.csv`. |
| Demanda | Unidades solicitadas, vendidas y no atendidas; tendencia y KPI 2. | `ventas_diarias.csv`, `solicitudes.csv` y `kpi_resumen.csv`. |
| Baja rotación | Referencias con bajo movimiento, datos insuficientes y KPI 3. | `inventario_actual.csv` y `kpi_resumen.csv`. |
| Pedidos y proveedores | Estados, respuestas, reintentos y KPI 4 y KPI 5. | `pedidos.csv` y `kpi_resumen.csv`. |

## Fuentes del proyecto

1. Equipo Demanda360. *Plan del MVP (versión aterrizada)*, 7 de noviembre de 2026, secciones 3, 4 y 6. Incluido en el paquete del equipo y en el PDF proporcionado.
2. Paquete del equipo: `07_por_integrante/3_Windows_datos_PowerBI/README.md`, tabla de datos simulados y tareas del rol 3.
3. *Demanda360. Entregable 1. Diagnóstico y proceso*, 13 de octubre de 2026, páginas 6 y 7: definición de los tres primeros KPI.
4. Repositorio local: `database/sql/01_schema.sql`, consultado el 8 de noviembre de 2026 para verificar los nombres de tablas y campos. La presencia del esquema no acredita ejecución ni valida por sí sola las vistas de KPI.
5. Sebastián. *Demanda360 · Estado del proyecto*, corte del 8 de noviembre de 2026 a las 16:30, apartados 3 y 4; y aclaración posterior del equipo sobre las cinco páginas temáticas.
6. Exportaciones simuladas `analytics/datos_demo/` y valores guardados de `analytics/consultas/verificacion_kpi.xlsx`, cotejados el 8 de noviembre de 2026.
