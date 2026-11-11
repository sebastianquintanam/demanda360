# Requerimientos funcionales y no funcionales · Demanda360

| Campo | Valor |
| --- | --- |
| Proyecto | Demanda360 – MVP para Pinturas By-plus |
| Documento | Matriz de requerimientos funcionales (RF) y no funcionales (RNF) |
| Versión | 1.4 |
| Fecha | 10 de noviembre de 2026 |
| Elaborado por | Jhonatan Stiben Rey Velásquez (Rol 4: frontend, prototipos, BPMN y requerimientos) |
| Estado | Actualización de evidencias posterior al PR #17, a la auditoría técnica del 8 nov 2026 (21:15) y a los PR #25 (riesgo inherente) y #26 (capturas `EV_BACKEND_03` a `EV_BACKEND_07`). Mantiene los 29 RF y 19 RNF, sus criterios de aceptación y los pendientes operativos y de video. Ver [sección 9.2](#92-pendientes-reales-y-cierres-de-la-auditoría). |
| Documento relacionado | [Trazabilidad de riesgos](trazabilidad_riesgos.md) |

---

## 1. Propósito y alcance

Este documento reúne los requerimientos del MVP de Demanda360 y muestra, para cada uno, de dónde sale, cómo se comprueba y en qué estado se encuentra. Su objetivo es que el equipo y el docente puedan ver con claridad qué está integrado en el código, qué se ha revisado y qué falta por verificar.

El alcance corresponde al plan del MVP: registro de productos, conteos, atenciones, entradas y ajustes; cálculo del saldo y del estado de cada producto; alerta de stock crítico con n8n; indicadores (KPI) y, como segunda etapa (P1), sugerencias de compra y pedidos con aprobación del propietario.

Este documento **no** demuestra que el sistema funcione. Separa cuatro cosas: el código integrado en el repositorio, las pruebas que reporta Quintana, la evidencia documental disponible y verificada, y las pruebas que todavía están pendientes.

## 2. Fuentes

| Código | Fuente | Fecha o versión | Uso en este documento |
| --- | --- | --- | --- |
| PLAN | Demanda360 — Plan del MVP (versión aterrizada) | 7 nov 2026 | Alcance, prioridades, reglas de cálculo, controles y criterios de aceptación (secciones 1 a 9) |
| CONTRATO | `docs/api/contrato.md` | Decisiones aprobadas el 8 nov 2026 | Rutas, reglas vigentes y estado de implementación declarado |
| README | `README.md` del repositorio | Versión entregada el 8 nov 2026 | Pantallas, pruebas, seguridad implementada y dueños de carpetas |
| AS-IS | BPMN AS-IS v3 (PR #4) | 8 nov 2026 | Proceso actual y fricciones MEDITA |
| TO-BE | `docs/bpmn/Demanda360_TO_BE_v4.bpmn`, su SVG y sus vistas V1 a V4 (`vistas_TO_BE_v4/`) | 8 nov 2026 (PR #10) | Actividades del proceso propuesto. El TO-BE v3 se conserva como versión histórica. |
| JUST | `docs/bpmn/justificacion_to_be_v4.md` | 8 nov 2026 (PR #10) | Relación entre fricciones y cambios. `justificacion_to_be.md` (v3) se conserva como versión histórica. |
| TALLER | Taller de Seguridad: Aplicación de ISO 27001 e ISO 27002 en Demanda360 | 4 nov 2026 | Riesgos, RTO y RPO propuestos, medidas de seguridad y ética |
| QUINTANA | Respuestas confirmadas por Quintana | 8 nov 2026 | Reglas de KPI, catálogos, cliente que regresa, ajustes, SIN_CONTEO y pedidos P1 |
| INFORME | `estado_demanda360_8nov.md`, informe de estado de Quintana (Rol 1) | 8 nov 2026 | Estado inicial de integración, pruebas y respuestas a diez preguntas de la versión 1.1 (sección 5) |
| AUDITORÍA | `auditoria_demanda360_8nov.md`, auditoría técnica de Quintana (Rol 1) | 8 nov 2026, 21:15 | Revisión posterior de `main` (PR #1–#20), CI, documentación y evidencias; diferencia implementación, capturas archivadas y demostración pendiente |

Para las **reglas funcionales vigentes**, prevalece el contrato de API. Para el **estado de implementación y evidencias al cierre**, prevalece la AUDITORÍA sobre el INFORME anterior. La auditoría fue realizada por Quintana; aquí se registra lo que documentó, sin atribuir al Rol 4 la ejecución de sus pruebas. Las diferencias relevantes se explican en la [sección 9](#9-diferencias-entre-documentos).

Abreviaturas usadas en la columna «Fuente»: «CONTRATO E1» y «CONTRATO E3» son las precisiones de las etapas 1 y 3; «CONTRATO P1» son las precisiones de pedidos; «CONTRATO n8n» es la tabla de la alerta de stock crítico. «TO-BE V1» a «TO-BE V4» son las vistas ampliadas del TO-BE v4.

## 3. Convenciones

### 3.1 Prioridad

| Prioridad | Significado según el plan |
| --- | --- |
| P0 | Obligatorio del MVP |
| P1 | Segunda etapa del MVP: sugerencias, pedidos, KPI 4 y 5, Power BI |
| P2 | Solo como propuesta futura; no tiene requerimiento ni criterio de aceptación (ver [sección 8](#8-fuera-de-alcance)) |

### 3.2 Estado de implementación

| Valor | Significado |
| --- | --- |
| Integrado | Funcionalidad o artefacto presente en `main` según el repositorio y la auditoría final. No implica que todos sus escenarios tengan captura individual. |
| Implementado con limitación | La función existe, pero el alcance del MVP es menor que el control operativo ideal (por ejemplo, solo cuentas de demostración). |
| Fuera del MVP / administrativo | No corresponde implementar una pantalla nueva: depende de procedimientos, responsables o de un futuro piloto. |
| Pendiente de material / confirmación | Falta un soporte o validación concreta; se describe cuál, sin convertirlo en funcionalidad inexistente. |

### 3.3 Estado de verificación

| Valor | Significado |
| --- | --- |
| Prototipo (mocks) | Captura en Live Server con datos simulados; prueba la visualización, no la API ni permisos del servidor. |
| Evidencia archivada | La captura, reporte o documento puede localizarse en el repositorio; se describe exactamente el escenario que respalda. |
| CI global documentada | La auditoría final y una captura respaldan 150 pruebas aprobadas con PostgreSQL; sin matriz prueba–RF/RNF **no se afirma** que cada criterio individual tenga evidencia de ejecución. |
| Reportado sin captura individual | Quintana documenta el escenario como probado, pero sigue pendiente su imagen o registro específico. |
| Pendiente de demo | El escenario está implementado y se programó mostrarlo durante la grabación; no hay captura particular del funcionamiento real. |
| Control administrativo pendiente | Requiere aprobación, procedimiento u operación fuera de las pruebas automáticas. |

> **Lectura correcta de las 150 pruebas.** `EV_BACKEND_01_150_pruebas_ci.png` y la AUDITORÍA documentan una ejecución satisfactoria de **150 pruebas** sobre `main`. La captura no permite asegurar por sí sola que cada criterio de aceptación esté cubierto. Las pantallas EV-R4 siguen siendo prototipos; el código Flask integrado se mostrará durante la demo.

### 3.4 Evidencias disponibles y localización

Se conservan los códigos EV de la v1.2 para evitar romper las referencias existentes. Los EV-01 a EV-06 son capturas históricas del prototipo y **no** equivalen a pruebas de backend. La versión 1.3 incorporó las evidencias localizadas tras el PR #17 y las señaladas por la auditoría; la versión 1.4 actualiza EV-22 con las cinco capturas integradas mediante el PR #26.

| Código | Evidencia | Estado y ubicación | Alcance verificable |
| --- | --- | --- | --- |
| EV-01 a EV-06 | Capturas anteriores del prototipo | Históricas, en materiales del Rol 4 | Visualización de mocks; **no** respuesta real de API. EV-06 representaba un 409 simulado. |
| EV-07 | Revisión visual del Rol 4 | Ahora respaldada por EV-17 | Pantallas Dashboard, Registro y Planificación con dos roles. |
| EV-08 | Cambiar cobertura de 14 a 7 días (54 → 24) | Reportado por Quintana; sin captura individual | Regla de cobertura; no dar por verificada visualmente. |
| EV-09 | Integración de PR en `main` | AUDITORÍA: PR #1–#20 integrados | Código fusionado; no equivale a prueba de interfaz. |
| EV-10 | BPMN AS-IS v3, TO-BE v4 y justificación | `docs/bpmn/` | Coherencia del modelo de proceso; no prueba la aplicación en ejecución. |
| EV-11 | Pruebas automatizadas del código | `backend/tests/`; resultado global en EV-13 | Existencia de pruebas; sin desglose exhaustivo prueba–requerimiento. |
| EV-12 | Informes técnicos de Quintana | `estado_demanda360_8nov.md` y `auditoria_demanda360_8nov.md` aportado por el equipo | Estado por cortes, alcance y escenarios por grabar. |
| EV-13 | 150 pruebas en verde | `docs/evidencias/EV_BACKEND_01_150_pruebas_ci.png` | Resultado global sobre `main`; respaldado por la auditoría. |
| EV-14 | Alerta con n8n y correo | `docs/evidencias/01_alerta_fallida_n8n_detenido.png`, `02_reintento_alerta_enviada.png`, `03_ejecucion_n8n_exitosa.png`, `04_correo_stock_critico_censurado.png`, `LEEME_evidencias.txt` | `FALLIDA` → reintento → `ENVIADA` y recepción de correo; las capturas no son ensayo de restauración. |
| EV-15 | Exportación CSV | `analytics/datos_demo/`, `analytics/consultas/comparacion_kpi_excel_csv.md` | AUDITORÍA cotejó `origen_datos=SIMULADO` en los CSV. |
| EV-16 | KPI de demostración | `analytics/powerbi/demanda360.pbix`, `docs/evidencias/powerbi/`, CSV y Excel de verificación | Auditoría cotejó cinco KPI: **27,3 %, 8,6 %, 50,0 %, 4,7 h, 66,7 %**. No son indicadores medidos en el comercio. |
| EV-17 | Seis capturas finales del Rol 4 | `docs/evidencias/EV_R4_01_dashboard_mock.png`, `EV_R4_02_registro_trabajador_mock.png`, `EV_R4_03_registro_propietario_mock.png`, `EV_R4_04_planificacion_propietario_superior_mock.png`, `EV_R4_04_planificacion_propietario_inferior_mock.png`, `EV_R4_05_planificacion_trabajador_mock.png` | Cinco comprobaciones visuales de **prototipo con datos simulados**; integradas mediante PR #17. |
| EV-18 | Conflicto por SKU repetido | `docs/evidencias/EV_BACKEND_02_error_409_sku_duplicado.png` | Captura de Flask en `localhost:8000` con consola `409 CONFLICT` y mensaje de SKU duplicado. **No** acredita `409 SIN_CONTEO`. |
| EV-19 | Respaldo y restauración aislada | `docs/evidencias/02_respaldo_postgresql.png`, `03_restauracion_verificada.png`, `docs/seguridad/registro_respaldos.md`; scripts en `scripts/` | Según AUDITORÍA, respaldo y restauración probada en entorno de ensayo; **no** acredita automáticamente RTO/RPO del negocio ni copias versionadas en cuenta separada. |
| EV-20 | Despliegue y controles de red | `docs/evidencias/01_despliegue_ubuntu.png`, `04_seguridad_bases.png` y evidencia de pruebas EV-13 | La auditoría registra puertos locales y controles automatizados; falta captura individual de algunos 401/403/CSRF. |
| EV-21 | Protección de secretos | Auditoría del historial Git y captura de evidencias (AUDITORÍA) | Sin `.env`, contraseñas, respaldos o correos reales expuestos, según revisión realizada por Quintana. |
| EV-22 | Alerta, reintento y segunda venta bajo umbral (nueva ejecución con base limpia) | `docs/evidencias/EV_BACKEND_03_registro_alerta_fallida.png`, `EV_BACKEND_04_reintento_alerta_enviada.png`, `EV_BACKEND_05_correo_recibido_censurado.png`, `EV_BACKEND_06_segunda_venta_sin_alerta.png`, `EV_BACKEND_07_una_sola_alerta_bd.png`; integradas mediante el PR #26 | Prueba ejecutada por Quintana en Flask (`localhost:8000`) con datos simulados: atención 90 (`SEL-MU-01`, saldo 11 → 3, umbral 3, estado Crítico, alerta `FALLIDA` con n8n detenido, evento `49c8aed8…`); `flask reintentar-alertas` → `ENVIADA` (intento 2) con el mismo `evento_id`; correo recibido con ese identificador; atención 91 (saldo 3 → 2, «Sin alerta»); consulta a `alertas_enviadas` con una sola fila `ENVIADA`, `intentos = 2`. Es una ejecución distinta de EV-14 (evento `361d2e61…`). Las capturas no muestran la fecha; el 10 nov es la fecha informada por Quintana. |

**Trazabilidad de lo pendiente:** los criterios 1, 3, 4, 7 y 13 aún necesitan fotogramas de la **aplicación real**. Los criterios 5 (venta) y 6 (saldo correcto) quedan respaldados por EV-22 para el caso de una venta con entrega; los rechazos 409 de la venta siguen sin captura individual. Las evidencias existentes del Rol 4 no se reemplazan por esas futuras capturas: se conservan identificadas como mocks y se añaden nuevas evidencias funcionales.

### 3.5 Criterios de demostración

La AUDITORÍA indica que **los 13 criterios tienen implementación** en `main`. Algunos ya cuentan con evidencia archivada (por ejemplo, 409 por SKU, venta y saldo con EV-22, alerta, KPI y respaldo), pero otros todavía carecen de capturas directas del escenario. Durante el video, el equipo debe mostrar y registrar **1, 3, 4, 7 y 13**. Esta distinción evita confundir *implementado* con *demostrado en la entrega*.

## 4. Actores

| Actor | Descripción |
| --- | --- |
| Propietario | Usuario con rol `propietario`. Crea productos, ajusta saldos, revisa sugerencias, aprueba y gestiona pedidos y consulta la auditoría. |
| Trabajador | Usuario con rol `trabajador`. Registra atenciones, conteos y entradas, y consulta información. |
| Ambos | Propietario y trabajador. |
| Sistema | Aplicación Flask con PostgreSQL. Valida, calcula y registra. |
| n8n | Automatización que recibe el evento de stock crítico y envía el correo. |
| Proveedor | Participante externo. No usa el sistema; se contacta por WhatsApp o llamada. |

## 5. Requerimientos funcionales

### 5.1 Acceso y catálogo

| ID | Nombre | Descripción | Prioridad | Actor | Fuente | Criterio de aceptación | Implementación | Verificación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RF-01 | Iniciar sesión | El usuario ingresa con su usuario y contraseña en `/login`. | P0 | Ambos | PLAN §4; CONTRATO; README | Con credenciales válidas entra a la aplicación. Una ruta `/api` sin sesión responde 401 `NO_AUTENTICADO`. | Integrado | CI global documentada; captura específica del 401 pendiente de demo. | EV-13 |
| RF-02 | Mostrar acciones según el rol | La pantalla oculta al trabajador las opciones reservadas al propietario. | P0 | Ambos | CONTRATO E1; PLAN §9 | Los elementos con clase `solo-propietario` no se muestran con rol trabajador. Ocultarlos es solo una comodidad visual: el control real es RNF-03. | Integrado | Prototipo (mocks): roles trabajador/propietario con capturas archivadas; protección de servidor se evalúa en RNF-03. | EV-17 |
| RF-03 | Crear producto | El propietario registra una referencia nueva; categoría, proveedor y unidad se eligen de las listas de `GET /api/catalogos`. | P0 | Propietario | PLAN §4; CONTRATO E3; QUINTANA | Producto válido → 201. SKU repetido → 409 `SKU_DUPLICADO`. Trabajador → 403 `SIN_PERMISO`. | Integrado | Evidencia archivada del 409 `SKU_DUPLICADO`; 201 de alta y 403 del trabajador pendientes de fotograma de demo. | EV-18, EV-13 |
| RF-04 | Consultar productos | Se consulta la lista de productos con su saldo y estado, y el detalle de un producto con sus últimos 10 movimientos. | P0 | Ambos | PLAN §4; CONTRATO E1 | El estado es uno de `SIN_CONTEO`, `AGOTADO`, `CRITICO`, `DATOS_INSUFICIENTES`, `BAJA_ROTACION` o `NORMAL`. Un `saldo: null` se muestra como «Sin conteo», nunca como 0. | Integrado | Prototipo (mocks) y CI global; consulta de API real sin captura individual del detalle. | EV-17, EV-13 |

### 5.2 Inventario

| ID | Nombre | Descripción | Prioridad | Actor | Fuente | Criterio de aceptación | Implementación | Verificación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RF-05 | Registrar conteo físico | Se registra la cantidad contada de un producto; el formulario envía un `origen_ref`. | P0 | Ambos | CONTRATO E3; QUINTANA; TO-BE V1 | Conteo válido → 201 con `saldo_anterior` y `saldo_actual`. Cantidad negativa o no entera → 400. Reenvío con el mismo `origen_ref` → 200 con `duplicado: true`. | Integrado | CI global documentada; conteo en la aplicación real pendiente de fotograma de demo. | EV-13, EV-17 |
| RF-06 | Calcular el saldo | El saldo se calcula como último conteo + entradas − ventas ± ajustes posteriores. No se guarda en ninguna tabla. | P0 | Sistema | PLAN §3; CONTRATO (`02_vistas.sql`) | Con un conteo de 5 y una venta de 2, el saldo queda en 3. Sin conteo, el saldo es `null`. | Integrado | Auditoría informa cálculo y pruebas en backend; saldo antes/después visible en la aplicación real para dos ventas (11 → 3 y 3 → 2). El caso de conteo seguido de venta no tiene captura propia. | EV-13, EV-12, EV-22 |
| RF-07 | Clasificar el estado del producto | El sistema asigna el estado en este orden: Sin conteo → Agotado → Crítico → Datos insuficientes → Baja rotación → Normal. | P0 | Sistema | PLAN §3; CONTRATO E1 y E3 | Con los datos demo, la respuesta de `GET /api/productos` es idéntica a su mock. Un producto contado después del corte queda en `DATOS_INSUFICIENTES`, salvo que esté agotado o crítico. | Integrado | Prototipo (mocks) y CI global; estados usados en datos demo. | EV-17, EV-13 |
| RF-08 | Registrar entrada de mercancía | Se registra la mercancía que llega y el saldo aumenta. | P0 | Ambos | PLAN §4; CONTRATO E3; TO-BE V4 | Cantidad mayor que 0 → 201 y el saldo sube. Producto que nunca se ha contado → 409 `SIN_CONTEO`. | Integrado | Prototipo (mocks) y CI global; caso específico `409 SIN_CONTEO` sin captura individual. | EV-17, EV-13 |
| RF-09 | Registrar ajuste justificado | El propietario corrige el saldo con una cantidad con signo y una justificación. | P0 | Propietario | PLAN §7; CONTRATO E3; QUINTANA | Cantidad distinta de 0. Justificación de 10 a 500 caracteres. Si deja el saldo negativo → 409 `STOCK_INSUFICIENTE`. Producto sin conteo → 409 `SIN_CONTEO`. Trabajador → 403. | Integrado | Prototipo (mocks), con opción de ajuste solo para propietario; CI global. | EV-17, EV-13 |

### 5.3 Atención al cliente y alertas

| ID | Nombre | Descripción | Prioridad | Actor | Fuente | Criterio de aceptación | Implementación | Verificación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RF-10 | Registrar la atención al cliente | En un solo registro se guarda lo que pidió el cliente y lo que recibió; si recibió algo, se genera la venta. | P0 | Ambos | PLAN §4; CONTRATO; TO-BE V3 | Entregado = 0 → se guarda como demanda no atendida y el saldo no cambia. Entregado mayor que el saldo → 409 `STOCK_INSUFICIENTE` y no se guarda nada. Entrega mayor que 0 en un producto sin conteo → 409 `SIN_CONTEO`. La respuesta trae `solicitud_id`, `no_atendida` y el bloque `producto`. | Integrado | Prototipo y CI global; atención con entrega registrada en la aplicación real (atenciones 90 y 91, con `solicitud_id` y bloque `producto`). Demanda no atendida, `409 STOCK_INSUFICIENTE` y `409 SIN_CONTEO` sin captura individual. | EV-17, EV-13, EV-22 |
| RF-11 | Relacionar al cliente que regresa | Cuando el cliente vuelve por lo que faltó, se elige su atención en la lista `faltantes_pendientes` y la venta se envía con `solicitud_previa_id`. | P0 | Ambos | CONTRATO E3 y decisión 2; QUINTANA | Misma referencia, enlazada a la atención original y con cantidad menor o igual al faltante; si no, 400. El regreso no suma a lo solicitado ni a lo no atendido (KPI 2), pero sus unidades sí cuentan como vendidas. | Integrado | Prueba automática en `backend/tests/test_api_inventario.py` (lista `faltantes_pendientes`, venta con `solicitud_previa_id` y 400 cuando supera el faltante), incluida en la CI global. La elección del faltante en pantalla sigue sin captura. | EV-12, EV-11, EV-13 |
| RF-12 | Generar la alerta de stock crítico | Cuando una venta hace que el saldo cruce el umbral, se crea una alerta. | P0 | Sistema | PLAN §3 y §5; CONTRATO n8n | Saldo antes > umbral ≥ saldo después → fila `PENDIENTE` en `alertas_enviadas` con `evento_id` único, en la misma transacción. Una segunda venta bajo el umbral no repite la alerta. | Integrado | Evidencia archivada del cruce del umbral (atención 90: 11 → 3 con umbral 3) y de la segunda venta bajo el umbral sin nueva alerta (atención 91: 3 → 2, «Sin alerta»), con una sola fila en `alertas_enviadas`. | EV-14, EV-22 |
| RF-13 | Enviar el correo de stock crítico | n8n recibe el evento con su token y envía el correo al equipo. | P0 | n8n | PLAN §5; CONTRATO n8n | Llega el correo y la alerta queda `ENVIADA`. Token inválido → 403. Si falla el envío, n8n responde 502 y la alerta queda `FALLIDA`. El correo incluye el `evento_id`. | Integrado (Flask y flujo de n8n, según el INFORME) | Evidencia de `ENVIADA`, n8n exitoso y correo recibido; respuesta 403 del webhook señalada por auditoría, pendiente de confirmar contexto específico. Segundo correo recibido con el `evento_id` de la nueva ejecución. | EV-14, EV-20, EV-22 |
| RF-14 | Reintentar alertas fallidas | El comando `flask reintentar-alertas` reenvía las alertas que no se enviaron. | P0 | Sistema | PLAN §5; CONTRATO n8n; README | Con n8n apagado, la venta se guarda y la alerta queda `FALLIDA`; al encender n8n y correr el comando, pasa a `ENVIADA`. Reenvía también las `PENDIENTE` de más de un minuto, con el mismo `evento_id` y máximo 3 intentos. Una `ENVIADA` nunca se reenvía. | Integrado | Evidencia archivada de `FALLIDA` → reintento → `ENVIADA` en dos ejecuciones, la segunda con el mismo `evento_id` e `intentos = 2`; alcance limitado a ambiente de ensayo. El límite de 3 intentos no tiene captura propia. | EV-14, EV-22 |

### 5.4 Consulta y auditoría

| ID | Nombre | Descripción | Prioridad | Actor | Fuente | Criterio de aceptación | Implementación | Verificación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RF-15 | Mostrar el Dashboard | Se muestran los KPI 1 a 3 con numerador, denominador y `detalle`, y la lista de productos críticos o agotados. | P0 | Ambos | CONTRATO; QUINTANA; TO-BE V1 | Con los datos demo y corte 2026-09-30: KPI 1 = 27,3 %, KPI 2 = 8,6 %, KPI 3 = 50 %. Un `corte` con formato inválido o una fecha futura → 400. Se ve la etiqueta «Datos simulados». | Integrado | Captura del Dashboard con mocks; KPI cotejados documentalmente entre cinco fuentes según auditoría; vista Flask real pendiente de video. | EV-17, EV-16 |
| RF-16 | Consultar rotación y cobertura | Por cada producto se consultan las unidades vendidas y no atendidas en 30 días, la cobertura en días y el plazo del proveedor. | P0 | Ambos | PLAN §4; CONTRATO | Responde los campos del mock de rotación; los productos con datos insuficientes traen `dias_con_registro`. | Integrado. **Solo API**: ni el CONTRATO ni el README la asocian a una pantalla. | Integrado como consulta API; CI global documentada, sin pantalla exclusiva ni captura individual de respuesta. | EV-13, EV-12 |
| RF-17 | Registrar la auditoría | Cada operación deja una fila en la tabla `auditoria`, dentro de la misma transacción. | P0 | Sistema | PLAN §7 y §9; CONTRATO P1 | Cada operación registrada deja su fila. En pedidos se registran `PEDIDO_CREADO`, `PEDIDO_APROBADO`, `PEDIDO_ENVIADO`, `PEDIDO_CONFIRMADO`, `PEDIDO_CANCELADO` y `PEDIDO_REINTENTO`. | Integrado | CI global documentada; auditoría funcional en pantalla pendiente de fotograma. | EV-13 |
| RF-18 | Consultar la auditoría | El propietario consulta las últimas operaciones registradas. | P0 | Propietario | PLAN §4 y §7 | `GET /api/auditoria` devuelve las últimas operaciones. Trabajador → 403. | Integrado. **Solo API**: ni el CONTRATO ni el README la asocian a una pantalla. | CI global documentada; prueba de rol y consulta real pendiente de fotograma de demo. | EV-13 |

### 5.5 Planificación de pedidos (P1)

| ID | Nombre | Descripción | Prioridad | Actor | Fuente | Criterio de aceptación | Implementación | Verificación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RF-19 | Calcular cantidades sugeridas | Se calcula cuánto pedir de cada producto con una fórmula visible y una cobertura ajustable entre 1 y 90 días (14 por defecto). | P1 | Propietario | PLAN §3; CONTRATO P1; TO-BE V1 | Con 14 días: laca catalizada alto brillo = 24 y total = 54. Cada línea trae `formula`. Con datos insuficientes, el sugerido es `null` y se define a mano. | Integrado | Prototipo muestra 14 días y sugeridos; auditoría coteja reglas de KPI y resultado; cambio a 7 días sin captura propia. | EV-17, EV-16, EV-08 |
| RF-20 | Crear el borrador del pedido | Se crea un pedido en estado `BORRADOR`; el servidor calcula la `cantidad_sugerida` de cada línea. | P1 | API: ambos roles. Pantalla Planificación: solo el propietario (decisión del MVP, [sección 10](#10-respuestas-y-decisiones-de-quintana)). | CONTRATO P1; PLAN §4; TO-BE V1 | Crea un `BORRADOR` con 1 a 50 líneas y sin productos repetidos; si no, 400. | Integrado | Prototipo (mocks) con acción solo de propietario; backend integrado y CI global documentada. | EV-17, EV-13 |
| RF-21 | Aprobar el pedido | El propietario pasa el pedido de borrador a aprobado. | P1 | Propietario | CONTRATO P1; TO-BE V1 | `BORRADOR → APROBADO` y queda registrado quién aprobó. Trabajador → 403 `SIN_PERMISO`. | Integrado | Prototipo (mocks) para propietario; verificación funcional específica pendiente de la demo/CI individual. | EV-17, EV-13 |
| RF-22 | Registrar el envío y la confirmación | Se registra que el pedido se envió al proveedor y, después, su confirmación. | P1 | Propietario | CONTRATO P1; TO-BE V2 | `APROBADO → ENVIADO` registra `fecha_envio`. `ENVIADO → CONFIRMADO` registra `fecha_respuesta` y `fecha_entrega_estimada`. Cualquier otro salto → 409 `TRANSICION_INVALIDA`. Confirmar no suma inventario. | Integrado | Prototipo (mocks) con estados de pedido; CI global y evidencia de alertas no sustituyen transición completa de pedido. | EV-17, EV-13 |
| RF-23 | Cancelar el pedido | El propietario cancela un pedido indicando el motivo. | P1 | Propietario | CONTRATO P1; TO-BE V2 | Se puede cancelar desde `BORRADOR`, `APROBADO` o `ENVIADO`, con un motivo de 5 a 300 caracteres. | Integrado | CI global documentada; captura individual de cancelación pendiente. | EV-13 |
| RF-24 | Reintentar con otro proveedor | Al cancelar, el propietario puede crear un nuevo intento del mismo pedido con un proveedor distinto. | P1 | Propietario | CONTRATO P1 y decisión 3; TO-BE V2 | Con `reintentar_con_proveedor_id` se crea un pedido nuevo con las mismas líneas, `numero_intento + 1`, `pedido_anterior_id` y estado `APROBADO`. Un pedido se reintenta una sola vez. | Integrado | CI global documentada; prueba del reintento de proveedor sin captura individual. | EV-13 |
| RF-25 | Consultar pedidos y tiempo de espera | Se consulta la lista de pedidos y, en los enviados sin respuesta, cuántas horas llevan esperando. | P1 | Ambos | CONTRATO P1; nota de TO-BE V2 | Devuelve los últimos 100 pedidos, del más nuevo al más viejo. Los `ENVIADO` sin respuesta traen `horas_esperando` (no es el plazo de entrega). | Integrado | Prototipo (mocks) muestra lista de pedidos a ambos roles; no acredita tiempos reales de espera. | EV-17 |

### 5.6 Analítica (P1)

| ID | Nombre | Descripción | Prioridad | Actor | Fuente | Criterio de aceptación | Implementación | Verificación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RF-26 | Calcular el KPI 4 | Se calcula el tiempo promedio, en horas, que tarda un proveedor en confirmar. | P1 | Sistema | PLAN §6; CONTRATO | Promedio de (respuesta − envío) de los pedidos con ambas fechas en el período. Los pedidos sin respuesta no se promedian; se cuentan aparte. | Integrado (vista SQL) | KPI 4 = 4,7 h cotejado entre SQL, CSV, Excel, fichas y Power BI según auditoría; datos demo. | EV-15, EV-16 |
| RF-27 | Calcular el KPI 5 | Se calcula el porcentaje de pedidos confirmados con el primer proveedor. | P1 | Sistema | PLAN §6; CONTRATO | Pedidos confirmados en el intento 1 / pedidos confirmados, contando cada cadena de reintentos una sola vez. | Integrado (vista SQL) | KPI 5 = 66,7 % cotejado entre SQL, CSV, Excel, fichas y Power BI según auditoría; datos demo. | EV-15, EV-16 |
| RF-28 | Exportar las vistas a CSV | El script `analytics/exportar_csv.sh` exporta las vistas para Power BI. | P1 | Sistema | PLAN §6; README | Los CSV quedan en `analytics/datos_demo/` y cada uno lleva la columna `origen_datos`. | Integrado: exportación CSV con marca `SIMULADO`, según AUDITORÍA | CSV disponibles; auditoría comprobó columna `origen_datos` con valor `SIMULADO`. | EV-15 |
| RF-29 | Visualizar los KPI en Power BI | Un tablero de cinco páginas muestra los cinco KPI a partir de los CSV. | P1 | Propietario | PLAN §6 | Muestra los cinco KPI con la marca «Datos simulados» y la hoja de verificación cuadra con las vistas. | Integrado: tablero de cinco páginas en `analytics/powerbi/demanda360.pbix`, según AUDITORÍA | Tablero `.pbix` de cinco páginas y capturas disponibles según auditoría; revisión final en video pendiente. | EV-16 |

## 6. Requerimientos no funcionales

| ID | Nombre | Descripción | Categoría | Prioridad | Fuente | Criterio de aceptación | Implementación | Verificación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RNF-01 | Autenticación con sesión | La sesión usa Flask-Login con cookie `HttpOnly` y vence a las 8 horas. | Seguridad | P0 | PLAN §7 (control 3); README; CONTRATO E3 | Una ruta sin sesión responde 401. En un `POST` sin sesión, el 401 aparece antes del chequeo de CSRF. | Integrado | CI global con familia de autenticación; prueba visual específica de 401 pendiente de grabación. | EV-13 |
| RNF-02 | Contraseñas con hash | Las contraseñas se guardan con hash (scrypt), nunca en texto plano. | Seguridad | P0 | PLAN §7 (control 4); README | La consulta a la tabla `usuarios` muestra solo hashes. | Integrado | Código documentado en README y CI global; la captura global no prueba por sí sola el algoritmo de hash. | EV-13, EV-12 |
| RNF-03 | Permisos verificados en el backend | Cada ruta verifica el rol en el servidor. Ocultar un botón no cuenta como control. | Seguridad | P0 | PLAN §4 y §7 (controles 5 y 6); CONTRATO | El trabajador recibe 403 `SIN_PERMISO` al crear un producto, ajustar, consultar sugeridos, aprobar, cambiar el estado de un pedido o consultar la auditoría. | Integrado | CI global documentada; captura específica de 403 trabajador pendiente de demo. | EV-13 |
| RNF-04 | Protección CSRF | Todo `POST` envía la cabecera `X-CSRFToken`. | Seguridad | P0 | PLAN §4; CONTRATO E1 | Token ausente o inválido → 400 `VALIDACION` con `campos: {"csrf": "invalido"}`. | Integrado | CI global documentada; sin captura individual del rechazo por CSRF. | EV-13 |
| RNF-05 | Validación de datos | Se valida el SKU único, que las cantidades sean enteras y que la unidad esté dentro de la lista. | Integridad | P0 | PLAN §7 (controles 1 y 2) | SKU repetido → 409. Cantidad inválida → 400. | Integrado | 409 por SKU duplicado comprobado en interfaz real y consola; rechazo de cantidad inválida pendiente de video. | EV-18, EV-13 |
| RNF-06 | Saldo consistente | La venta se registra en una transacción que bloquea la fila del producto (`SELECT … FOR UPDATE`). | Integridad | P0 | PLAN §3 | Una venta mayor que el saldo responde 409 y no guarda nada; el saldo nunca queda negativo. | Integrado | CI global documentada; venta con saldo correcto visible en la aplicación real (EV-22). El rechazo 409 de una venta mayor que el saldo sigue sin captura individual. | EV-13, EV-22 |
| RNF-07 | Sin registros duplicados | Cada formulario genera un `origen_ref` para evitar que un reenvío cree dos registros. | Integridad | P0 | PLAN §4; CONTRATO E3 y P1 | Reenvío → 200 con `duplicado: true`. Un `origen_ref` usado en otro tipo de registro → 409 `ORIGEN_REF_EN_USO`. En pedidos, que no tienen `origen_ref`, el botón se bloquea mientras guarda. | Integrado | CI global documentada; `origen_ref` y caso específico de duplicado sin captura individual. | EV-13 |
| RNF-08 | Manejo uniforme de errores | Todos los errores usan el formato `{"error": {"codigo", "mensaje", "campos"}}` y nunca muestran trazas. | Seguridad | P0 | PLAN §4; CONTRATO E1 | El 500 trae `error.referencia` igual a la cabecera `X-Request-ID`. Un método no permitido → 405 `METODO_NO_PERMITIDO`. | Integrado | CI global documentada; respuesta de error 409 visible, no demuestra todos los formatos 400/405/500. | EV-18, EV-13 |
| RNF-09 | Movimientos inmutables y bitácora | Los movimientos no se borran ni se editan; las correcciones se hacen con ajustes. La auditoría es de solo inserción. | Integridad | P0 | PLAN §7 (controles 7 y 8); README | Un movimiento existente no se puede borrar ni modificar. | Integrado | Auditoría y CI documentadas; intento de `UPDATE` bloqueado pendiente de grabación. | EV-13, EV-12 |
| RNF-10 | Continuidad de la venta ante fallas de n8n | Una falla en el envío de la alerta no afecta la venta ya registrada. | Disponibilidad | P0 | PLAN §5; CONTRATO n8n | Si n8n está apagado, responde 502 o no contesta en 10 s, la venta queda guardada y la alerta queda `FALLIDA`. | Integrado | Capturas de la alerta FALLIDA y su reintento; `EV_BACKEND_03` muestra la venta guardada (saldo 11 → 3) con la alerta `FALLIDA` y n8n detenido; no se midió por separado el timeout de 10 s. | EV-14, EV-12, EV-22 |
| RNF-11 | Secretos fuera del repositorio | Las credenciales viven solo en `.env`. | Seguridad | P0 | PLAN §7 (control 9); README | `.env` está fuera de Git y `.env.example` no tiene valores. | Integrado | Auditoría de todo el historial Git sin secretos reales según Quintana; `.env.example` solo contiene ejemplos. | EV-21 |
| RNF-12 | Servicios no expuestos a la red | Los servicios solo escuchan en el equipo local y n8n se protege con token. | Seguridad | P0 | PLAN §2 y §7; README | Puertos atados a `127.0.0.1`; PostgreSQL no responde desde otro equipo de la red; el webhook rechaza un token inválido; la app corre sin privilegios de root en el contenedor. | Integrado | Captura del despliegue local y revisión reportada de 403 de webhook; sin atribuir a estas imágenes todos los controles de red. | EV-20, EV-13 |
| RNF-13 | Respaldo y restauración probada | Se hace un respaldo con `pg_dump` fuera del repositorio y se comprueba que se puede restaurar. | Disponibilidad | P0 | PLAN §7; TALLER §9 a §11 | Se restaura en una base de prueba aislada (`demanda360_restore`), sin afectar la base de trabajo del equipo; se comparan los conteos de las tablas y el saldo de tres referencias, y se anota la duración. El RTO de 4 horas y el RPO de 1 hora son **objetivos propuestos en el TALLER, sujetos a un simulacro**; no son resultados. | Integrado: `scripts/backup.sh` y `scripts/restore_prueba.sh` con evidencia de restauración aislada según AUDITORÍA | Restauración de prueba y respaldo documentados con capturas; los objetivos RTO/RPO siguen sin acreditarse como tiempos reales del negocio. | EV-19 |
| RNF-14 | Minimización de datos personales | El sistema no guarda datos de clientes; el contacto del proveedor es opcional (Ley 1581 de 2012). | Privacidad | P0 | PLAN §5 y §7 (control 11); TALLER §13 | No hay campos de datos de clientes. El correo de alerta lleva solo SKU, nombre, saldo, umbral y plazo. | Integrado | Captura de correo de stock crítico sin datos de clientes; cobertura total de privacidad no comprobada solo con esa imagen. | EV-14 |
| RNF-15 | Datos rotulados y reglas transparentes | La interfaz indica el origen de los datos que muestra y cada sugerencia explica su cálculo. | Ética y transparencia | P0 | PLAN §1 y §7; CONTRATO | La etiqueta «Datos simulados» se muestra en el modo con mocks y cuando las respuestas traen `origen_datos: SIMULADO`. Con datos reales, la interfaz no los identifica como simulados. Cada sugerido trae su `formula`. | Integrado (rotulado de datos simulados) | Pantallas y CSV con etiqueta `SIMULADO`; no constituye evidencia de datos reales. | EV-17, EV-15 |
| RNF-16 | Formularios que conservan lo escrito | Ante un error, el formulario muestra el mensaje de la API sin borrar lo que el usuario escribió. | Usabilidad | P0 | PLAN §9; CONTRATO | Se muestra el mensaje del 400 o del 409 y se conservan los datos. La justificación del ajuste exige 10 caracteres también en la pantalla. | Integrado | Error real de SKU duplicado mostrado por la API y campos conservados en el formulario. | EV-18 |
| RNF-17 | Lógica en un solo lugar | Las pantallas comparten el mismo JavaScript y los cálculos oficiales viven en `database/sql/02_vistas.sql`. | Mantenibilidad | P0 | CONTRATO; README | Prototipos y plantillas cargan los mismos `comun.js`, `dashboard.js`, `registro.js` y `planificacion.js`. | Integrado | Código compartido integrado según `main` y revisión de auditoría; prototipos conservados. | EV-09, EV-17 |
| RNF-18 | Control de versiones e integración continua | Los cambios entran a `main` solo por pull request y las pruebas corren en GitHub. | Mantenibilidad | P0 | PLAN §7 (control 12); README | Todo cambio entra por PR con una aprobación y las pruebas en verde. | Integrado según el README | PR #1–#20 integrados en `main`; PR #17 aprobado; 150 pruebas en verde con evidencia de CI. | EV-09, EV-13 |
| RNF-19 | Despliegue con Docker Compose | El sistema se levanta con un solo comando. | Despliegue | P0 | PLAN §9; README | `docker compose up -d` levanta `db`, `web` y `n8n`. `GET /api/health` responde `{"estado":"ok","bd":"ok"}`. | Integrado | Despliegue Ubuntu documentado; app Flask utilizada en captura HTTP 409; `health` sin fotograma individual. | EV-20, EV-18 |

**Rendimiento.** Ningún documento define una métrica de rendimiento, así que no se incluye un RNF de esa categoría. La única cifra de tiempo documentada es la espera máxima de 10 segundos de la alerta, y ya forma parte de RNF-10. Si el equipo define un valor, se agregará en una versión posterior.

## 7. Actividades manuales del TO-BE

Estas actividades aparecen en el TO-BE v4, pero se hacen fuera del sistema, así que no se convierten en requerimientos funcionales:

- Hacer el conteo físico. Su registro es RF-05.
- Revisar las sugerencias y decidir qué comprar.
- Enviar el pedido por WhatsApp o llamada. El sistema solo registra el estado `ENVIADO` (RF-22).
- Esperar la respuesta del proveedor: revisar a los 30 minutos y, como máximo, una hora después del primer contacto con cada proveedor. El sistema solo muestra las horas de espera (RF-25).
- Elegir otro proveedor cuando el primero no responde o no tiene disponibilidad. El registro del nuevo intento es RF-24.

## 8. Fuera de alcance

**Propuestas P2 del plan (sin requerimiento ni criterio de aceptación):** IA predictiva, WhatsApp oficial, envío automático de pedidos, servicios en la nube y multiempresa.

**Medidas del TALLER que no se convierten en requerimientos del MVP.** Se tratan como controles administrativos o como propuestas, y su relación con los riesgos está en [trazabilidad_riesgos.md](trazabilidad_riesgos.md):

- Autenticación multifactor en cuentas de administración (8.5). La aplicación no la tiene; solo está configurada en las cuentas de GitHub.
- Alertas por ajustes masivos, repetidos o fuera de horario (8.15 y 8.16). El MVP solo alerta por stock crítico.
- Restauración mensual y copias versionadas en una cuenta separada (8.13).
- Capacitación para identificar mensajes falsos y reportar eventos (6.3 y 6.8).
- Controles físicos del puesto de trabajo y del celular (7.7 a 7.9).

## 9. Diferencias entre documentos

### 9.1 Resueltas

| # | Diferencia | Cómo quedó |
| --- | --- | --- |
| 1 | `GET /api/catalogos` no estaba en el plan. | El CONTRATO la define para ambos roles (`categorias`, `proveedores`, `unidades_medida`); Quintana confirmó que ya figura en la fila 13 de su tabla de rutas (decisión 6). |
| 2 | La tabla `conteos_fisicos` del plan no tiene `origen_ref`. | El CONTRATO indica que el conteo envía `origen_ref` y agrega el error `ORIGEN_REF_EN_USO`; Quintana confirmó que la columna existe como `varchar(64)` y tiene la restricción `UNIQUE` `uq_conteos_origen_ref` (decisión 7). |
| 3 | `solicitud_previa_id` no estaba en la tabla `solicitudes_clientes` del plan. | El CONTRATO define `faltantes_pendientes` en `GET /api/productos/{id}` y la regla del cliente que regresa (decisión 2 del CONTRATO). |
| 4 | El plan no nombraba el código de error para productos sin conteo. | `409 SIN_CONTEO` en entradas, ajustes y ventas con entrega mayor que 0. |
| 5 | Texto de los KPI: `nota` o `detalle`. | Queda `detalle`. |
| 6 | KPI 1: 27 % o 27,3 %. | El CONTRATO y el README usan 27,3 %. El plan (§6 y §9) todavía dice 27 %; prevalece el CONTRATO. |
| 7 | Si el nuevo intento con otro proveedor necesita otra aprobación. | El reintento nace `APROBADO` por el propietario que lo pide y se permite una sola vez. |
| 8 | Formato de identificadores y prioridades del README del Rol 4 (RF01, solo P0 y P1). | Se usa RF-01 y RNF-01; lo P2 va como lista aparte. |
| 9 | Crear borradores: la API acepta ambos roles, pero en la pantalla solo el propietario tiene «Guardar borrador». | Decisión aceptada para el MVP (decisión 1). No requiere cambios en el código. |
| 10 | Espera máxima de la alerta: 3 s en el plan y 10 s en el CONTRATO. | Se mantiene la espera de 10 s del CONTRATO (decisión 10). El plan conserva el valor anterior. |
| 11 | El TO-BE v3 y `justificacion_to_be.md` decían que P1 no estaba implementado y conservaban pendientes que el CONTRATO ya resolvió. | Resuelto con el TO-BE v4 y `justificacion_to_be_v4.md`, incorporados mediante el PR #10 ([sección 11](#11-cierre-de-los-cambios-del-to-be)). La v3 se conserva como histórico. |
| 12 | Si rotación, auditoría y los KPI 4 y 5 debían tener pantalla, y si la edición del umbral y del contacto del proveedor entraba al MVP. | La rotación y la auditoría quedan como API sin pantalla propia; los KPI 4 y 5 van a SQL, CSV y Power BI; editar umbrales y contactos queda fuera del MVP (decisiones 2, 3 y 4). |

### 9.2 Pendientes reales y cierres de la auditoría

La versión 1.2 se cerró antes de que entraran las últimas evidencias. La siguiente tabla sustituye las nueve tareas que se mostraban como abiertas, **sin borrar la historia**: separa las resueltas documentalmente de las demostraciones aún pendientes.

| # v1.2 | Asunto | Estado a corte 8 nov, 21:15 (filas 3, 6, 7 y 9 actualizadas al 10 nov) | Responsable / siguiente paso |
| --- | --- | --- | --- |
| 1 | Power BI cinco páginas (RF-29) | **Documentado como completado**: `analytics/powerbi/demanda360.pbix` y `docs/evidencias/powerbi/`; KPI coincidentes según AUDITORÍA. | Olmer: verificar visualización y consolidar documento final. |
| 2 | Respaldo y restauración (RNF-13) | **Con evidencia archivada**: `02_respaldo_postgresql.png`, `03_restauracion_verificada.png` y `docs/seguridad/registro_respaldos.md`. No afirmar RTO/RPO cumplidos. | Sebastián/Brayan: mostrar resultado en el video si el plan lo incluye. |
| 3 | Riesgo inherente R1–R6 | **Documentado (10 nov).** Brayan valoró y justificó los seis riesgos en `docs/seguridad/evaluacion_riesgo_inherente.md`; la trazabilidad v1.4 los incorporó sin cambiar los residuales (PR #25). Sigue siendo una propuesta académica pendiente de validación con los propietarios. | Equipo y propietarios: validar las valoraciones; no modificar los valores sin acuerdo. |
| 4 | Evidencia de seguridad 401/403/CSRF/red/token | **Parcial documentada**: puertos locales, evidencia de webhook y suite CI. Falta material visual individual de parte de los controles. | Quintana y Brayan: grabar 403 del trabajador y otros escenarios definidos en la demo; no inventar capturas. |
| 5 | Prueba de 150 casos y CI | **Documentada**: `EV_BACKEND_01_150_pruebas_ci.png`, CI en verde según AUDITORÍA. | Equipo: conservar la salida y, si se solicita, relacionar cada prueba con su criterio. |
| 6 | Prueba real de n8n | **Documentada**: cuatro capturas del escenario `FALLIDA` → reintento → `ENVIADA` y correo. | Cerrado con EV-22 (PR #26): nueva ejecución con `FALLIDA`, reintento `ENVIADA`, correo, segunda venta «Sin alerta» y una sola fila en `alertas_enviadas`. |
| 7 | Trece criterios de demostración | **Los 13 implementados**, según AUDITORÍA; **faltan fotogramas** de 1, 3, 4, 7 y 13. Los criterios 5, 6 y 8 tienen capturas de la aplicación real (EV-22 y EV-14). | Equipo: grabar app real y adjuntar capturas de esos momentos en otro PR. |
| 8 | Métrica general de rendimiento | **Limitación declarada.** No hay línea base de negocio ni prueba global de rendimiento aprobada. | Equipo: no presentar un valor inventado ni agregar RNF sin acuerdo. |
| 9 | Selector de faltantes pendientes (RF-11) | **Sin captura individual.** Existe prueba automática en `backend/tests/test_api_inventario.py`, cubierta por la CI global. | Rol 4: incluirlo brevemente en la demo si resulta viable; si no, registrarlo como escenario pendiente de comprobación. |

**Otras limitaciones que siguen vigentes:** cuentas demo compartidas por rol (no cuentas individuales), controles administrativos de verificación de proveedor y folios de contingencia aún por formalizar, y datos de prueba simulados. La grabación debe utilizar la aplicación Flask real y distinguirla de las capturas antiguas con mocks.

## 10. Respuestas y decisiones de Quintana

Las diez preguntas planteadas en la versión 1.1 fueron respondidas por Sebastián Quintana en la sección 5 del informe `estado_demanda360_8nov.md` (corte del 8 de noviembre de 2026). Las respuestas se registran como decisiones del equipo; las verificaciones y evidencias aún faltantes se mantienen identificadas en las secciones 3 y 9.2.

### 10.1 Decisiones del MVP

1. **Borradores (RF-20).** La API permite que ambos roles creen borradores: un trabajador puede proponer un pedido. La pantalla Planificación es exclusiva del propietario porque utiliza los sugeridos, que solo él consulta. Aprobar, enviar, confirmar y cancelar corresponde únicamente al propietario. Se conserva esta diferencia como decisión del MVP; no se cambia el código.
2. **Rotación y auditoría (RF-16 y RF-18).** Permanecen como funcionalidades de la API y como evidencia, sin una pantalla dedicada. La baja rotación aparece como estado del producto en el Dashboard. El propietario consulta la auditoría mediante `GET /api/auditoria` (criterio 13 de la demo).
3. **KPI 4 y 5 (RF-26 y RF-27).** No se muestran en el Dashboard de Flask, que presenta los KPI 1 a 3. Los KPI 4 y 5 están en la vista SQL, en `kpi_resumen.csv` y se visualizarán en Power BI. Para los datos de demostración: KPI 4 = **4,7 horas** (promedio de tres pedidos con respuesta; dos enviados sin respuesta se excluyen del promedio) y KPI 5 = **66,7 %** (dos de tres pedidos).
4. **Edición del umbral y contacto del proveedor.** Su modificación queda fuera del MVP. La limitación se registra en los riesgos R4 y R6; no se inventan rutas ni pantallas para administrarlos.
5. **Respaldo y restauración (RNF-13).** En el INFORME inicial faltaban scripts y registros; **la AUDITORÍA posterior ya documenta** `scripts/backup.sh`, `scripts/restore_prueba.sh`, las capturas de respaldo y restauración, y `docs/seguridad/registro_respaldos.md`. Sebastián desarrolló los scripts y Brayan aportó evidencias. El ensayo no prueba cumplimiento operativo de RTO/RPO ni respaldo permanente en cuenta separada.

### 10.2 Aclaraciones documentales o de evidencia

6. **`GET /api/catalogos` en el contrato.** Quintana confirmó que ya aparece en la **fila 13** de la tabla de rutas de `docs/api/contrato.md`. Se cierra esta observación.
7. **Columna `origen_ref` en `conteos_fisicos`.** Quintana confirmó que existe como `varchar(64)` y tiene restricción `UNIQUE` denominada `uq_conteos_origen_ref`.
8. **CI y cobertura de pruebas.** Según Quintana, la CI ejecuta `pytest` con **PostgreSQL 16** en cada PR; se reportan 150 pruebas satisfactorias. Las familias documentadas son `test_auth` (inicio de sesión y 401), `test_roles` (403), `test_api_inventario` (productos, conteos, ventas, movimientos, 400 y 409), `test_esquema` (reglas de base de datos), `test_seguridad` (CSRF y errores sin trazas), `test_alertas` (alerta y reintentos), `test_api_analitica` y `test_kpi_demo` (KPI), `test_api_pedidos` (P1) y `test_pantallas` (interfaces). **La ejecución global de CI ya tiene captura** (`EV_BACKEND_01_150_pruebas_ci.png`) y la AUDITORÍA reporta 150 pruebas en verde sobre `main`; esta distribución por archivos todavía **no equivale** a una matriz completa prueba–requerimiento.
9. **Protección de `main`.** Quintana confirmó que está activa: los cambios entran mediante PR y requieren aprobación de un revisor de `CODEOWNERS`. Esto se complementa con la captura de CI (EV-13); son evidencias diferentes.
10. **Tiempo de espera de n8n.** Prevalece el contrato: Flask espera **10 segundos como máximo**, no los 3 segundos del plan inicial. Quintana informó que la ejecución real de n8n tardó **2,8 segundos**, incluido el envío mediante Gmail. Es una medición reportada, no una garantía general de rendimiento.

## 11. Cierre de los cambios del TO-BE

Los diez ajustes previstos en la versión 1.1 para el diagrama y los cuatro previstos para la justificación quedaron incorporados en `Demanda360_TO_BE_v4.bpmn`, su SVG, las cuatro vistas de `vistas_TO_BE_v4/` y `justificacion_to_be_v4.md`. Según el INFORME, estos archivos entraron a `main` mediante el PR #10. El AS-IS y el TO-BE v3 no se modificaron y se conservan como histórico.

El Rol 4 revisó visualmente el diagrama general, las cuatro vistas y la justificación v4; Claude reportó validación técnica con bpmnlint y bpmn-js. No se ha ejecutado una comprobación técnica independiente del archivo `.bpmn` en esta revisión.

### 11.1 Diagrama `Demanda360_TO_BE_v4.bpmn`

| # | Ajuste previsto | Estado | Cómo quedó en la v4 |
| --- | --- | --- | --- |
| 1 | Leyenda de P1 | Resuelto | La leyenda indica que Dashboard, Registro y Planificación están integrados en `main` y que falta comprobarlos contra PostgreSQL. |
| 2 | Reintento sin nueva aprobación | Resuelto | Nota: «Un pedido se reintenta una sola vez… Nace APROBADO, así que no vuelve a la aprobación inicial». |
| 3 | Condición de reintento único | Resuelto | Compuerta «¿Es el primer intento y hay otro proveedor disponible?»; si no, el pedido termina cancelado. |
| 4 | 409 `SIN_CONTEO` en la atención | Resuelto | Salida «Rechazo: producto sin conteo (409 SIN_CONTEO)» cuando se entrega más de 0; se quitó la nota pendiente. |
| 5 | 409 `SIN_CONTEO` en la entrada | Resuelto | Compuerta «¿El producto tiene conteo?» con el rechazo antes de actualizar el saldo. |
| 6 | Cliente que regresa | Resuelto | La nota usa `faltantes_pendientes` y `solicitud_previa_id`. |
| 7 | Confirmar no suma inventario | Resuelto | Nota: «Confirmar no suma inventario: el saldo sube cuando la mercancía llega y se registra su entrada». |
| 8 | Nota de alertas | Resuelto | Respuestas 200, 502 y 403 de n8n, espera máxima de 10 s y reintento posterior de las `FALLIDA` y las `PENDIENTE` de más de un minuto, hasta 3 intentos. |
| 9 | Carril de «Crear el borrador del pedido» | Resuelto por decisión | La tarea queda en el carril del propietario, lo que coincide con la decisión 1: la pantalla Planificación es exclusiva del propietario. La nota del diagrama todavía rotula el tema como «Pendiente (RF-20)»; este documento registra la decisión y el diagrama no se vuelve a modificar. |
| 10 | Vistas ampliadas | Resuelto | Las cuatro vistas se regeneraron en `vistas_TO_BE_v4/`. |

### 11.2 `justificacion_to_be_v4.md`

| # | Ajuste previsto | Estado | Cómo quedó |
| --- | --- | --- | --- |
| 1 | Sección 3: estado actual | Resuelto | Indica que el código está integrado en `main` y que las revisiones con mocks no demuestran el funcionamiento contra PostgreSQL. |
| 2 | Sección 4: columna de evidencia | Resuelto | Las fricciones I, E y T presentan los beneficios como esperados y separan el código integrado de lo comprobado. |
| 3 | Sección 6: reglas | Resuelto | Incluye `SIN_CONTEO` y el reintento único con otro proveedor. |
| 4 | Sección 7: pendientes | Resuelto | Marca como resueltos los dos pendientes de la v3 y conserva la observación de que el plan solo define alertas por ventas. |

> La justificación v4 se escribió antes del INFORME inicial y la AUDITORÍA. Por eso puede conservar pendientes históricos como RF-20 y no reflejar las capturas nuevas de n8n. La decisión funcional vigente sobre RF-20 sigue en la sección 10; no se altera retrospectivamente el BPMN aprobado.

## 12. Historial de cambios

| Versión | Fecha | Cambio | Autor |
| --- | --- | --- | --- |
| 1.0 | 8 nov 2026 | Primera versión: 29 RF, 19 RNF, diferencias, preguntas y cambios pendientes del TO-BE. | Jhonatan Rey (Rol 4) |
| 1.1 | 8 nov 2026 | Se distingue la ubicación de las evidencias (carpeta compartida o GitHub) y el estado de cada PR. Se precisa el rotulado de datos simulados en RNF-15. | Jhonatan Rey (Rol 4) |
| 1.2 | 8 nov 2026 | Se incorpora el informe de estado de Quintana: PR #1 a #10 en `main`, pantallas conectadas a la API real, 150 pruebas reportadas, prueba real de n8n, CSV de los KPI y valores de KPI 4 y 5. Se agrega el estado «Prueba reportada», la columna «Tipo» y las evidencias EV-12 a EV-16. Se actualizan los estados de RF-12 a RF-14, RF-20, RF-26 a RF-29, RNF-10, RNF-12, RNF-13 y RNF-18 sin cambiar criterios de aceptación. La sección 10 incorpora las diez respuestas textuales sintetizadas del informe de Quintana, y la sección 9 separa lo resuelto de los pendientes reales y la sección 11 cierra los ajustes del TO-BE con la v4 (PR #10). Las referencias al modelo vigente pasan del TO-BE v3 al v4. | Jhonatan Rey (Rol 4) |
| 1.3 | 8 nov 2026 | Conciliación con auditoría final de Quintana (21:15): PR #1–#20, 150 pruebas con captura, evidencia de error real 409, n8n, KPI/Power BI, respaldo y restauración, seguridad y cinco pruebas visuales del Rol 4. Se cierran pendientes documentales de la v1.2 sin borrar limitaciones ni convertir mocks en pruebas de backend. Se mantienen pendientes los fotogramas de la demo, la confirmación de RF-11 y los riesgos inherentes a cargo de Brayan. No cambian los 29 RF, 19 RNF ni sus criterios. | Jhonatan Rey (Rol 4) |
| 1.4 | 10 nov 2026 | Actualización de estados de evidencia tras los PR #25 y #26: EV-22 pasa a las capturas `EV_BACKEND_03` a `EV_BACKEND_07`; se actualizan las columnas de verificación y evidencia de RF-06, RF-10 a RF-14, RNF-06 y RNF-10; la sección 9.2 cierra el riesgo inherente (documentado por Brayan) y la captura de la segunda venta, y precisa RF-11; los fotogramas pendientes pasan a los criterios 1, 3, 4, 7 y 13. Se corrige el enlace a la sección 9.2. No cambian los 29 RF, 19 RNF ni sus criterios de aceptación. | Jhonatan Rey (Rol 4) |
