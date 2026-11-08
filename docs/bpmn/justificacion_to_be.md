# Justificación del BPMN TO-BE de Demanda360

**Proyecto:** Demanda360 – MVP para Pinturas By-plus
**Modelo:** `Demanda360_TO_BE_v3.bpmn` (vistas ampliadas en `vistas_TO_BE_v3/`)
**Base:** BPMN AS-IS v3 y Plan del MVP (versión aterrizada)
**Fecha:** 8 de noviembre de 2026

## 1. Propósito

En este documento se explica cómo el proceso propuesto (TO-BE) responde a las fricciones MEDITA identificadas en el proceso actual (AS-IS). Para cada fricción se indica qué cambia, en qué parte del diagrama aparece y qué efecto se espera. Además, se distingue con claridad entre lo que ya está comprobado y lo que todavía es un beneficio esperado.

## 2. Alcance del modelo

El TO-BE tiene un proceso principal y dos procesos operativos relacionados:

- **Proceso principal: planificación y generación de pedidos.** Empieza con la necesidad de revisar el abastecimiento y termina en *Pedido confirmado*. También puede terminar sin pedido, o con el pedido cancelado cuando no hay otro proveedor disponible.
- **Proceso operativo: atención al cliente y alerta de stock crítico (P0).** Registra lo que pidió el cliente y lo que recibió, incluida la demanda no atendida, y genera la alerta cuando corresponde.
- **Proceso relacionado: entrada de mercancía (P0).** Actualiza el saldo cuando llega la mercancía. No hace parte obligatoria del flujo principal.

Participantes: Propietario, Trabajador, Demanda360 (aplicación Flask y PostgreSQL), Demanda360 (n8n) y Proveedor como participante externo.

## 3. Convenciones

| Marca | Significado |
|---|---|
| [P0] | Obligatorio del MVP. Está en desarrollo; por ahora solo se ha probado en prototipos con datos simulados. |
| [P1] | Funcionalidad prevista para una etapa posterior. **No está implementada.** |
| [Manual] | Se hace fuera del sistema. |
| Beneficio **esperado** | Mejora que se espera lograr cuando la función esté integrada y en uso. |
| Beneficio **comprobado** | Mejora que ya se verificó con evidencia (prueba, captura o ejecución). |

Estado comprobado a la fecha: los prototipos de **Dashboard** y **Registro** se validaron localmente con Live Server y datos simulados (commit `5c90f3a`, rama `feature/frontend`). Todavía no están integrados con Flask ni con PostgreSQL. Por eso ninguna regla del backend (saldo, alertas, estados del pedido) se considera comprobada en este documento.

## 4. Fricción → cambio → efecto

| Fricción MEDITA (AS-IS) | Cambio en el TO-BE | Dónde aparece en el BPMN | Prioridad | Efecto esperado | Comprobado a la fecha |
|---|---|---|---|---|---|
| **M – Manual:** el conteo de existencias se hace a mano en cada revisión. | El conteo físico sigue existiendo, pero ahora es **condicional** y queda registrado. El saldo se calcula a partir del último conteo, las ventas, las entradas y los ajustes. | *¿Es necesario hacer un conteo físico?* → *Hacer y registrar el conteo físico* (vista 1). | P0 | Hacer menos conteos completos y contar solo cuando haya que verificar existencias. La fricción **se reduce, no se elimina**. | El formulario de conteo existe en el prototipo de Registro, con datos simulados. El cálculo del saldo aún no se ha comprobado. |
| **I – Información:** no se registran las ventas por producto, así que no se sabe qué rota más o menos. | Cada atención registra lo solicitado y lo entregado, **incluida la demanda no atendida**. El tablero muestra existencias, estado y rotación. Las cantidades sugeridas se calculan con una fórmula visible. | *Registrar lo que pidió el cliente y lo que recibió* (vista 3); *Revisar existencias y rotación en el tablero* (vista 1); *Calcular las cantidades sugeridas* (vista 1). | P0 (registro y tablero) · P1 (sugeridos) | Tomar decisiones de compra con datos por producto y medir referencias agotadas, demanda no atendida y baja rotación (KPI 1 a 3). | Los prototipos de Dashboard y Registro muestran y capturan esta información con datos simulados. Los KPI y las sugerencias aún no se han comprobado con datos reales ni con el backend. |
| **E – Espera:** se espera la respuesta del proveedor sin saber cuánto tarda; la entrega toma de 2 a 5 días. | La espera **sigue siendo manual**: 30 minutos y, como máximo, una hora desde el primer contacto con cada proveedor. Se agrega la alerta de stock crítico para detectar faltantes antes. El tiempo de confirmación se podrá medir con el KPI 4. | *Esperar la respuesta del proveedor*, *Pasan 30 minutos sin respuesta* y *¿Ya pasó una hora...?* (vista 2); alerta en n8n (vista 3). | P0 (alerta) · P1 (medición del tiempo) | Iniciar el pedido antes de quedarse sin producto y tener datos sobre el tiempo de respuesta. **La espera del proveedor no se elimina**, porque depende de él. | No comprobado. La alerta con n8n y la medición del tiempo de respuesta están pendientes de integración. |
| **T – Trazabilidad:** no hay un registro organizado de pedidos, respuestas de proveedores ni productos agotados. | El pedido pasa por estados con fecha (BORRADOR, APROBADO, ENVIADO, CONFIRMADO o CANCELADO, con motivo). Cada cambio de proveedor queda enlazado como un nuevo intento. Las operaciones quedan en la auditoría y las alertas guardan su estado (PENDIENTE, ENVIADA o FALLIDA). | *Crear el borrador*, *Aprobar*, *Enviar... y marcarlo como ENVIADO*, *Registrar la confirmación*, *Registrar la cancelación* y *Preparar el nuevo intento* (vistas 1 y 2). | P1 (pedidos) · P0 (auditoría y alertas) | Poder consultar qué se pidió, a quién, cuándo y con qué resultado, y medir los pedidos confirmados con el primer proveedor (KPI 5). | No comprobado. Los pedidos son P1 y no están implementados; la auditoría y el estado de las alertas siguen en desarrollo. |
| **D – Duplicidad potencial:** cuando la lista se hace en papel, puede que haya que escribirla otra vez para enviarla por WhatsApp. No ocurre en todos los pedidos. | El pedido se arma como borrador en el sistema a partir de las sugerencias. El envío al proveedor sigue siendo por WhatsApp o llamada. | *Crear el borrador del pedido* y *Enviar el pedido por WhatsApp o llamada* (vistas 1 y 2). | P1 | Evitar la lista en papel y tener una sola fuente para el pedido. La fricción **se reduce en parte**, porque el mensaje al proveedor se sigue escribiendo a mano. | No comprobado. El borrador de pedido es P1. |

> En el AS-IS no se identificó la fricción **A (actividad inútil)** de MEDITA, por eso no aparece en la tabla.

## 5. Lo que sigue siendo manual

- Contactar al proveedor por WhatsApp o por llamada.
- Controlar la espera: revisar a los 30 minutos y, como máximo, a la hora del primer contacto con cada proveedor. El sistema solo muestra cuántas horas lleva el pedido sin respuesta.
- Elegir otro proveedor cuando el primero no tiene disponibilidad o no responde.
- Hacer el conteo físico cuando sea necesario.

## 6. Reglas que el modelo respeta

- **Demanda no atendida:** si el cliente pide 5 unidades y se le entregan 0, la atención se guarda y el saldo no cambia. El error 409 aparece solo cuando se intenta entregar más de lo disponible.
- **Alertas:** se generan solo cuando una venta deja el saldo en el umbral o por debajo, si antes estaba por encima. No se repiten con las ventas siguientes. Si el correo falla, la venta sigue guardada y la alerta queda FALLIDA. Los reintentos no son inmediatos: se hacen después con el comando `flask reintentar-alertas`, con un máximo de 3 intentos.
- **Cambio de proveedor:** si no hay otro proveedor disponible, el pedido termina como CANCELADO.

## 7. Pendientes por confirmar con Quintana

1. Si un nuevo intento con otro proveedor necesita otra aprobación. Por ahora el diagrama lo reenvía sin aprobar de nuevo.
2. Cómo validar una entrega cuando el producto está SIN_CONTEO, es decir, con el saldo vacío.
3. Observación: el plan solo define alertas por ventas. No dice nada sobre alertas por conteos, entradas o ajustes, así que el modelo no las incluye.

## 8. Cómo se comprobarán los beneficios

Según el plan del MVP, los beneficios esperados se podrán comprobar con:

- Pruebas de la venta con alerta, incluido el caso con n8n apagado: la venta se guarda, la alerta queda FALLIDA y, después del reintento, pasa a ENVIADA.
- Capturas de la ejecución en n8n, del correo recibido y de la fila de la alerta.
- Cálculo de los KPI 1 a 3 con los datos simulados de septiembre. El plan prevé una prueba automática para validarlos.
- Para las funciones P1 (sugerencias y pedidos), las evidencias se agregarán cuando se implementen. Hasta entonces, sus beneficios se presentan solo como esperados.
