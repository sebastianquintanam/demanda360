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

## Evidencia del movimiento en Power BI

Las cinco capturas acreditan la visualización de los indicadores del corte simulado de septiembre. La prueba de que una operación posterior se refleja en Power BI sigue pendiente. El inventario de septiembre muestra saldo **11** para `SEL-MU-01`. El informe de estado del 8 de noviembre describe una venta de demostración que dejó el saldo en **3**. [CSV de inventario del corte de septiembre](../../../analytics/datos_demo/inventario_actual.csv)

Para cerrar esa prueba se necesita una exportación desde la base que contiene la venta y con un corte que la incluya. El registro de evidencia debe identificar la operación, el SKU, el corte y el saldo de la fila exportada. Luego se refresca una copia del informe con los CSV de ese mismo corte, se verifica el saldo en Disponibilidad y se guarda una captura donde el corte esté identificado. La evidencia se incorpora junto con la referencia a la operación y al archivo exportado.
