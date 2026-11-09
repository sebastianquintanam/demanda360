# Demanda360 — Evidencias de Power BI

**Responsable:** rol 3, datos y Power BI  
**Período:** 1 al 30 de septiembre de 2026  
**Corte:** 30/09/2026 · **Datos simulados**

Las capturas documentan los resultados del tablero de cinco páginas. Resumen y Disponibilidad se capturaron desde el informe final guardado como `.pbix`. Las tres páginas restantes se capturaron después de actualizar los datos en el proyecto que dio origen al informe final. [Informe de Power BI](../../../analytics/powerbi/demanda360.pbix) · [Cotejo con Excel y CSV](../../../analytics/consultas/comparacion_kpi_excel_csv.md)

| Página | Resultado visible | Evidencia |
| --- | --- | --- |
| Resumen | Las tarjetas muestran 27,3 % de referencias agotadas, 8,6 % de demanda no atendida, 50,0 % de baja rotación, 4,7 h de confirmación y 66,7 % de confirmación con el primer proveedor. La tabla muestra las bases de los cinco indicadores. | [01 · Resumen](01_resumen.png) |
| Disponibilidad | De 11 referencias, 3 están agotadas, 2 críticas, 5 en baja rotación y 1 tiene datos insuficientes. Se muestra el saldo y la comparación de cobertura con el plazo del proveedor. | [02 · Disponibilidad](02_disponibilidad.png) |
| Demanda | 139 unidades solicitadas, 127 vendidas y 12 no atendidas. El porcentaje es 8,6 %. Se muestran la tendencia diaria y la comparación por SKU. | [03 · Demanda](03_demanda.png) |
| Baja rotación | 5 de 10 referencias evaluables dan 50,0 %. La laca transparente tiene 3 días de registro y se presenta aparte como datos insuficientes. | [04 · Baja rotación](04_baja_rotacion.png) |
| Pedidos y proveedores | Los tiempos de 3, 6 y 5 horas dan 4,7 h en promedio. Dos de las tres cadenas confirmadas se resolvieron con el primer proveedor. La tabla distingue los intentos confirmado, cancelado y enviado. | [05 · Pedidos y proveedores](05_pedidos_y_proveedores.png) |

## Evidencia del movimiento en Power BI · Criterio 9

**Atención 90 · SEL-MU-01 · Corte 08/11/2026 · Datos simulados**

La atención se registró el **8 de noviembre de 2026 a las 15:53:56**, hora de Bogotá, para el sellador para muros cuñete. Sebastián entregó la exportación del estado posterior a la atención, obtenida del respaldo de las **16:30** del mismo día. Los dos CSV de esta prueba se cargaron en un proyecto de Power BI separado. [06 · Captura verificada en Power BI](atencion_90/06_atencion_90_2026-11-08.jpg)

| Comprobación | Resultado | Fuente |
| --- | --- | --- |
| Atención registrada | Se solicitaron y entregaron **8 unidades**, con **0** unidades sin atender. | [solicitudes.csv](atencion_90/solicitudes.csv), fila con `solicitud_id = 90`. |
| Inventario posterior | El saldo es **3 unidades**, el umbral es **3** y el estado es **`CRITICO`**. | [inventario_actual.csv](atencion_90/inventario_actual.csv), fila con `sku = SEL-MU-01`. |
| Conciliación del saldo | El saldo previo reconstruido es **11 = 3 + 8**, coherente con el cambio **11 → 3** registrado en la auditoría de la demo. | Reconciliación de las dos filas y del informe de estado del equipo del 8 de noviembre. |

La captura verifica que Power BI refleja el saldo posterior de esa operación al cargar los dos CSV. Las cinco páginas de indicadores se documentan arriba con el corte simulado de septiembre, del 1 al 30. El corte del 8 de noviembre se usa para esta comprobación puntual del movimiento.
