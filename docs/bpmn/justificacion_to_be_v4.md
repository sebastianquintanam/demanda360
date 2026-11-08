# Justificación del BPMN TO-BE de Demanda360 (v4)

**Proyecto:** Demanda360 – MVP para Pinturas By-plus
**Modelo:** `Demanda360_TO_BE_v4.bpmn` (vistas ampliadas en `vistas_TO_BE_v4/`)
**Base:** BPMN AS-IS v3, Plan del MVP, `CONTRATO.md` vigente (precisiones de las etapas 1 y 3, pedidos P1 y alerta con n8n) y `requerimientos.md` v1.0
**Fecha:** 8 de noviembre de 2026
**Reemplaza a:** `justificacion_to_be.md` (versión v3, que se conserva sin cambios)

## 1. Propósito

En este documento se explica cómo el proceso propuesto (TO-BE) responde a las fricciones MEDITA identificadas en el proceso actual (AS-IS). Para cada fricción se indica qué cambia, en qué parte del diagrama aparece, qué efecto se espera y qué evidencia existe hasta hoy. Se mantiene la diferencia entre un beneficio **esperado** y uno **comprobado**: tener el código integrado no significa que su funcionamiento esté comprobado.

## 2. Alcance del modelo

El TO-BE tiene un proceso principal y dos procesos operativos relacionados:

- **Proceso principal: planificación y generación de pedidos.** Empieza con la necesidad de revisar el abastecimiento y termina en *Pedido confirmado*. También puede terminar sin pedido, o con el pedido cancelado sin reintento.
- **Proceso operativo: atención al cliente y alerta de stock crítico (P0).** Registra lo que pidió el cliente y lo que recibió, incluida la demanda no atendida, valida el conteo y el saldo, y genera la alerta cuando corresponde.
- **Proceso relacionado: entrada de mercancía (P0).** Actualiza el saldo cuando llega la mercancía, siempre que el producto ya tenga un conteo.

Participantes: Propietario, Trabajador, Demanda360 (aplicación Flask y PostgreSQL), Demanda360 (n8n) y Proveedor como participante externo. Los carriles, los flujos manuales y los temporizadores de 30 minutos y una hora son los mismos de la v3.

## 3. Convenciones y estado actual

| Marca | Significado |
|---|---|
| [P0] | Funcionalidad obligatoria del MVP. |
| [P1] | Funcionalidad de segunda prioridad (sugerencias y pedidos). |
| [Manual] | Se hace fuera del sistema. |
| Beneficio **esperado** | Mejora que se espera lograr cuando la función se use con datos reales. |
| Beneficio **comprobado** | Mejora verificada con evidencia de funcionamiento (prueba ejecutada, captura o registro contra el backend real). |

**Estado a la fecha.** Según lo informado por el equipo, el código de Dashboard, Registro y Planificación está integrado en `main` mediante el PR #5 (Dashboard y Registro con la API real) y el PR #6 (pedidos P1 y Planificación) (EV-09). Esto prueba que el código está integrado, **no que funcione**. Las revisiones propias del Rol 4 se hicieron con mocks y Live Server (EV-01 a EV-07); las pruebas visuales con mocks no demuestran el funcionamiento real contra PostgreSQL. Por eso, en este documento ninguna regla del backend (saldo, `SIN_CONTEO`, alertas, estados del pedido) se presenta como comprobada.

Códigos de evidencia (definidos en `requerimientos.md`, sección de evidencias):

| Código | Evidencia | Qué demuestra |
|---|---|---|
| EV-01 a EV-06 | Capturas del prototipo (Dashboard, Registro por rol, ajuste y error 409 simulado) | Pantallas con mocks. No prueban el backend. |
| EV-07 | Revisión visual del Rol 4 (8 nov 2026) de las tres pantallas con ambos roles | Sin registro guardado. |
| EV-08 | Reporte de Quintana: con cobertura de 7 días, el sugerido total pasa de 54 a 24 | Dato reportado, sin captura. |
| EV-09 | PR #5 y PR #6 fusionados en `main`, según el equipo | Integración del código, no su funcionamiento. |
| EV-11 | `backend/tests/test_kpi_demo.py`, nombrado en el contrato y el README | Prueba declarada; no se ha revisado su resultado. |

## 4. Fricción → cambio → efecto

| Fricción MEDITA (AS-IS) | Cambio en el TO-BE | Dónde aparece en el BPMN | Prioridad | Efecto esperado | Evidencia disponible y limitaciones |
|---|---|---|---|---|---|
| **M – Manual:** el conteo de existencias se hace a mano en cada revisión. | El conteo físico sigue existiendo, pero es **condicional** y queda registrado. El saldo se calcula con el último conteo, las ventas, las entradas y los ajustes. Un producto que nunca se ha contado no acepta entregas ni entradas (409 `SIN_CONTEO`). | *¿Es necesario hacer un conteo físico?* → *Hacer y registrar el conteo físico* (vista 1); compuertas *¿El producto tiene conteo?* (vistas 3 y 4). | P0 | Hacer menos conteos completos y contar solo cuando haya que verificar existencias. La fricción **se reduce, no se elimina**. | Código integrado (EV-09). El formulario de conteo y el estado «Sin conteo» se revisaron con mocks (EV-02, EV-03, EV-07). El 409 solo se simuló en pantalla (EV-06). El cálculo del saldo contra PostgreSQL no está comprobado. |
| **I – Información:** no se registran las ventas por producto, así que no se sabe qué rota más o menos. | Cada atención registra lo solicitado y lo entregado, **incluida la demanda no atendida** (entregado = 0). El cliente que regresa se enlaza con su atención original. El tablero muestra existencias, estado y rotación, y las cantidades sugeridas se calculan con una fórmula visible. | *Registrar lo que pidió el cliente y lo que recibió* y nota del cliente que regresa (vista 3); *Revisar existencias y rotación en el tablero* y *Calcular las cantidades sugeridas* (vista 1). | P0 (registro y tablero) · P1 (sugeridos) | Decidir las compras con datos por producto y medir referencias agotadas, demanda no atendida y baja rotación (KPI 1 a 3). | Código integrado (EV-09). Dashboard y Registro se revisaron con mocks (EV-01, EV-03, EV-04, EV-07). Los KPI tienen una prueba declarada cuyo resultado no se ha revisado (EV-11). El cambio de cobertura (7 días → 24) es un dato reportado (EV-08). Nada de esto se ha comprobado con datos reales. |
| **E – Espera:** se espera la respuesta del proveedor sin saber cuánto tarda; la entrega toma de 2 a 5 días. | La espera **sigue siendo manual**: 30 minutos y, como máximo, una hora desde el primer contacto con cada proveedor. El sistema muestra las horas que lleva cada pedido ENVIADO sin respuesta. La alerta de stock crítico avisa antes de quedarse sin producto. | *Esperar la respuesta del proveedor*, *Pasan 30 minutos sin respuesta* y *¿Ya pasó una hora...?* (vista 2); alerta con n8n (vista 3). | P0 (alerta) · P1 (horas de espera) | Iniciar el pedido antes de agotar el producto y tener datos sobre el tiempo de respuesta (KPI 4). **La espera del proveedor no se elimina**, porque depende de él. | Código integrado (EV-09). La lista de pedidos se revisó con mocks (EV-07). La alerta con n8n figura como implementada en el contrato, pero no hay captura del correo, de la ejecución en n8n ni de la fila de la alerta. No comprobado. |
| **T – Trazabilidad:** no hay un registro organizado de pedidos, respuestas de proveedores ni productos agotados. | Se propone que los pedidos tengan estados y fechas de seguimiento (BORRADOR, APROBADO, ENVIADO, CONFIRMADO o CANCELADO con motivo). Si se cambia de proveedor, se crea **un único reintento**: un pedido nuevo enlazado al anterior que nace APROBADO. Las alertas guardan su estado (PENDIENTE, ENVIADA o FALLIDA) y el número de intentos. | *Crear el borrador*, *Aprobar*, *Enviar... y marcarlo como ENVIADO*, *Registrar la confirmación*, *Cancelar con motivo y crear el reintento* y *Cancelar el pedido y registrar el motivo* (vistas 1 y 2); estados de la alerta (vista 3). | P1 (pedidos) · P0 (auditoría y alertas) | Consultar qué se pidió, a quién, cuándo y con qué resultado, y medir los pedidos confirmados con el primer proveedor (KPI 5). | Código integrado (EV-09). Aprobación, envío y confirmación solo se revisaron de forma visual y por rol (EV-07). La cancelación y el reintento no tienen ninguna verificación. No comprobado. |
| **D – Duplicidad potencial:** cuando la lista se hace en papel, puede que haya que escribirla otra vez para enviarla por WhatsApp. No ocurre en todos los pedidos. | El pedido se arma como borrador en el sistema a partir de las sugerencias. El envío al proveedor sigue siendo por WhatsApp o llamada. | *Crear el borrador del pedido* y *Enviar el pedido por WhatsApp o llamada* (vistas 1 y 2). | P1 | Evitar la lista en papel y tener una sola fuente para el pedido. La fricción **se reduce en parte**, porque el mensaje al proveedor se sigue escribiendo a mano. | Código integrado (EV-09); pantalla revisada con mocks (EV-07). Queda pendiente qué rol puede crear borradores (sección 7). No comprobado. |

> En el AS-IS no se identificó la fricción **A (actividad inútil)** de MEDITA, por eso no aparece en la tabla.

## 5. Lo que sigue siendo manual

- Contactar al proveedor por WhatsApp o por llamada.
- Controlar la espera: revisar a los 30 minutos y, como máximo, a la hora del primer contacto con cada proveedor. El sistema solo muestra cuántas horas lleva el pedido ENVIADO sin respuesta; no avisa ni cambia de proveedor por sí solo.
- Elegir otro proveedor cuando el primero no tiene disponibilidad o no responde.
- Hacer el conteo físico cuando sea necesario.

## 6. Reglas que el modelo respeta

- **Demanda no atendida:** si el cliente pide 5 unidades y se le entregan 0, la atención se guarda como demanda no atendida y el saldo no cambia. Este caso no exige conteo previo.
- **Producto sin conteo:** si se intenta entregar una cantidad mayor que 0 de un producto que nunca se ha contado, el registro se rechaza con 409 `SIN_CONTEO`. Lo mismo pasa con una entrada de mercancía, que se rechaza antes de actualizar el saldo.
- **Falta de saldo:** si se intenta entregar más de lo disponible, el registro se rechaza con 409 `STOCK_INSUFICIENTE` y no se guarda nada.
- **Cliente que regresa:** la pantalla muestra la lista de faltantes pendientes del producto (`faltantes_pendientes`, atenciones de los últimos 30 días con faltante sin cubrir). Se escoge la atención original y la venta se envía con su `solicitud_previa_id`. La cantidad no puede superar el faltante pendiente y no cuenta como demanda nueva.
- **Confirmación del pedido:** confirmar registra la fecha de respuesta y la fecha estimada de entrega, pero **no suma inventario**. El saldo sube cuando la mercancía llega y se registra su entrada (vista 4).
- **Cambio de proveedor:** al cancelar con motivo se puede crear un reintento con un proveedor distinto. El reintento es un pedido nuevo con las mismas líneas, el siguiente número de intento y enlazado al anterior; nace APROBADO por el propietario que lo pide, así que no vuelve a la aprobación inicial. Un pedido se reintenta **una sola vez**: si el reintento tampoco funciona, o no hay otro proveedor, el pedido termina CANCELADO.
- **Alertas:** se generan solo cuando una venta deja el saldo en el umbral o por debajo, si antes estaba por encima, y no se repiten con las ventas siguientes. La alerta se guarda como PENDIENTE junto con la venta. Después, Flask avisa a n8n y espera la respuesta **10 segundos como máximo**. n8n responde 200 con `ok:true` solo después de enviar el correo, 502 si el envío falla y 403 si el token no es válido. Solo con 200 y `ok:true` la alerta pasa a ENVIADA; en otro caso queda FALLIDA, se suma un intento y se guarda el error. La venta nunca se deshace.
- **Reintentos de alertas:** no son inmediatos. Se hacen después con el comando `flask reintentar-alertas`, que reenvía las alertas FALLIDAS y las PENDIENTES con más de un minuto, con el mismo `evento_id` y hasta 3 intentos. Una alerta ENVIADA nunca se reenvía.

## 7. Pendientes y observaciones

1. **Quién crea los borradores (RF-20), pendiente con Quintana.** El contrato permite que ambos roles creen borradores, pero en la pantalla revisada solo el propietario puede hacerlo. El diagrama deja la tarea en el carril del propietario con una nota y no propone una solución hasta que se decida.
2. **Observación:** el plan solo define alertas por ventas. No dice nada sobre alertas por conteos, entradas o ajustes, así que el modelo no las incluye.
3. **Diferencia de tiempo de espera de la alerta:** el plan mencionaba 3 segundos y el contrato fija 10 segundos. El modelo usa el valor del contrato.

Quedan resueltos, según el contrato vigente, los dos pendientes de la v3: el reintento no necesita otra aprobación (nace APROBADO) y la entrega sobre un producto sin conteo se rechaza con 409 `SIN_CONTEO`.

## 8. Cómo se comprobarán los beneficios

Según el plan del MVP y el contrato, los beneficios esperados se podrán comprobar con:

- Pruebas de la venta con alerta, incluido el caso con n8n apagado: la venta se guarda, la alerta queda FALLIDA y, después de `flask reintentar-alertas`, pasa a ENVIADA.
- Capturas de la ejecución en n8n, del correo recibido y de la fila de la alerta.
- Pruebas de los rechazos 409 `SIN_CONTEO` y `STOCK_INSUFICIENTE` contra el backend real, no solo simulados en pantalla.
- Revisión del resultado de `test_kpi_demo.py` (KPI 1 a 3 con los datos simulados de septiembre).
- Para pedidos (P1): pruebas del recorrido borrador → aprobado → enviado → confirmado, de la cancelación con motivo y del reintento único con otro proveedor.

Hasta que existan esas evidencias, todos los beneficios de la sección 4 se presentan como **esperados**.

## 9. Diferencias con la v3

| # | Cambio | Dónde |
|---|---|---|
| 1 | Leyenda y convenciones: P0 y P1 tienen código integrado en `main` (PR #5 y #6), revisado solo con mocks y sin verificación contra PostgreSQL. Se quita «P1 no está implementado». | Leyenda del diagrama y de las vistas; secciones 3 y 4 |
| 2 | Cambio de proveedor: la compuerta pasa a «¿Es el primer intento y hay otro proveedor disponible?». *Preparar el nuevo intento* se reemplaza por *Cancelar con motivo y crear el reintento con el otro proveedor*, que vuelve al envío como pedido APROBADO. Se quita la nota pendiente sobre otra aprobación y se agrega una nota con la regla del reintento único. | Vista 2 |
| 3 | Atención al cliente: nuevo orden de validaciones: ¿se entregó alguna unidad? (no → demanda no atendida), ¿el producto tiene conteo? (no → 409 `SIN_CONTEO`), ¿se entrega más de lo disponible? (sí → 409 `STOCK_INSUFICIENTE`). Se quita la nota pendiente sobre SIN_CONTEO. | Vista 3 |
| 4 | Entrada de mercancía: nueva compuerta «¿El producto tiene conteo?» con el rechazo 409 `SIN_CONTEO` antes de actualizar el saldo. | Vista 4 |
| 5 | Cliente que regresa: la nota usa `faltantes_pendientes` y `solicitud_previa_id`. | Vista 3 |
| 6 | Confirmación: nueva nota «Confirmar no suma inventario» junto a *Pedido confirmado*. La tarea indica el estado CONFIRMADO. | Vista 2 |
| 7 | Alertas: la compuerta pregunta si n8n confirmó el envío en 10 segundos o menos; nota con las respuestas 200, 502 y 403; *Marcar como FALLIDA* guarda el error; el reintento es una tarea separada (*Reenviar más tarde con flask reintentar-alertas*) con nota sobre FALLIDAS, PENDIENTES de más de un minuto y máximo 3 intentos. | Vista 3 |
| 8 | Nota pendiente RF-20 junto a *Crear el borrador del pedido*. | Vista 1 |
| — | Presentación: carriles de la aplicación y de n8n más altos para que nada se superponga; nuevas vistas en `vistas_TO_BE_v4/`. | Todo el modelo |
