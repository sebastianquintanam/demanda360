# Demanda360 — Comparación del Excel con los CSV

**Responsable:** rol 3, datos y Power BI.  
**Fecha del cotejo:** 8 de noviembre de 2026.  
**Período de los datos:** 1 al 30 de septiembre de 2026.  
**Corte:** 30/09/2026.  
**Origen:** DATOS SIMULADOS.

## Resultado

Los cinco KPI coinciden al mostrarse con un decimal.

| KPI | Base recalculada desde el detalle | Excel guardado | kpi_resumen.csv | Recálculo del detalle | Cotejo |
| --- | --- | --- | --- | --- | --- |
| KPI1 | 3 / 11 | 27,3 % | 27,3 % | 27,3 % | Coincide. |
| KPI2 | 12 / 139 | 8,6 % | 8,6 % | 8,6 % | Coincide. |
| KPI3 | 5 / 10 | 50,0 % | 50,0 % | 50,0 % | Coincide. |
| KPI4 | 14 / 3 | 4,7 h | 4,7 h | 4,7 h | Coincide. |
| KPI5 | 2 / 3 | 66,7 % | 66,7 % | 66,7 % | Coincide. |

Las cuatro tasas se comparan como porcentajes y el KPI 4 como horas. El Excel conserva la precisión de sus divisiones; `kpi_resumen.csv` presenta un decimal. No se sustituyeron resultados del Excel por cifras escritas manualmente para forzar coincidencias.

## Método y archivos

1. Se leyeron los resultados calculados y guardados en `analytics/consultas/verificacion_kpi.xlsx`, hoja `Datos_simulados.`, celdas D16:D20. Se verificaron sus equivalentes a un decimal frente al resumen CSV.
2. Se recalculó KPI 1 con los saldos verificados de `inventario_actual.csv`. No se interpretan los saldos vacíos como cero. El inventario tiene una fila por referencia y sus SKU son únicos.
3. Se recalculó KPI 2 desde `solicitudes.csv`, usando únicamente las atenciones con `cuenta_en_kpi2 = SI`, sumando solicitado menos entregado y dividiendo entre solicitado.
4. Se recalculó KPI 3 desde el inventario: numerador con saldo positivo, de 0 a 2 vendidas y 30 días completos; denominador con conteo y 30 días completos. La laca transparente queda fuera por sus 3 días de registro.
5. Se recalculó KPI 4 desde las diferencias entre `fecha_respuesta` y `fecha_envio` de `pedidos.csv`. Hay tres respuestas: 3, 6 y 5 horas. Los intervalos suman 14 horas; 14 / 3 se presenta como 4,7 h.
6. Se recalculó KPI 5 con las cadenas confirmadas de `pedidos.csv`. Son tres cadenas distintas: dos confirmadas en intento 1 y una en intento 2. Los intentos cancelados y los pendientes no aumentan el denominador.

## Controles adicionales

- Unidades vendidas en `ventas_diarias.csv`: **127**.
- Unidades no atendidas en `ventas_diarias.csv`: **12**.
- Total calculado de `sugerido_14d`: **54 unidades**; no incluye la cantidad manual de la laca transparente.
- Todos los registros de los cinco CSV revisados indican `origen_datos = SIMULADO`.
- Los porcentajes se presentan con un decimal; no se suman porcentajes, numeradores o denominadores de KPI diferentes en una fila de total.

## Lectura correcta de los pedidos sin respuesta

El pedido 2 está **CANCELADO** y el pedido 5 está **ENVIADO**. Ambos carecen de fecha de respuesta y se excluyen del promedio. Solo uno permanece actualmente pendiente. La descripción de «dos enviados sin respuesta» se debe interpretar como dos intentos que tuvieron envío, no como dos pedidos actualmente pendientes.

## Evidencia de la operación en Power BI

El cotejo de indicadores usa los CSV del 30 de septiembre de 2026. La atención 90 se verificó en un proyecto separado con `inventario_actual.csv` y `solicitudes.csv` del corte del 8 de noviembre. Power BI mostró 8 unidades entregadas de `SEL-MU-01`, saldo posterior 3 y estado `CRITICO`. El saldo anterior de 11 se reconstruyó como 3 + 8 y coincide con la auditoría. [Evidencia y CSV de la atención 90](../../docs/evidencias/powerbi/README.md#evidencia-del-movimiento-en-power-bi--criterio-9)

## Alcance de esta comprobación

Este registro acredita coherencia aritmética entre los CSV y los resultados guardados en Excel. No ejecuta un recálculo dentro de Excel ni las consultas de PostgreSQL. Las pruebas del backend y su resultado se sustentan en las evidencias del líder técnico.

El informe final contiene las cinco páginas del corte de septiembre. Las capturas y la evidencia del movimiento del 8 de noviembre se encuentran en el [índice de evidencias de Power BI](../../docs/evidencias/powerbi/README.md).

Los datos son una demostración simulada: no prueban mejoras económicas reales ni constituyen una línea base real de Pinturas By-plus.

## Referencias del proyecto

- Los cinco archivos de `analytics/datos_demo/`: `inventario_actual.csv`, `ventas_diarias.csv`, `solicitudes.csv`, `pedidos.csv` y `kpi_resumen.csv`.
- `analytics/consultas/verificacion_kpi.xlsx`, versión guardada revisada en este cotejo.
- `docs/requerimientos/kpi.md`, definición de los cinco indicadores.
- *Demanda360 · Estado del proyecto*, corte del 8 de noviembre de 2026 a las 16:30, apartado de Olmer (rol 3) y criterios 9 y 10 de la demostración.
