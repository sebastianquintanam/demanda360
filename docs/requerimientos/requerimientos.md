# Requerimientos funcionales y no funcionales · Demanda360

| Campo | Valor |
| --- | --- |
| Proyecto | Demanda360 – MVP para Pinturas By-plus |
| Documento | Matriz de requerimientos funcionales (RF) y no funcionales (RNF) |
| Versión | 1.1 |
| Fecha | 8 de noviembre de 2026 |
| Elaborado por | Jhonatan Stiben Rey Velásquez (frontend, prototipos, BPMN y requerimientos) |
| Estado | En revisión con Quintana (Rol 1) |
| Documento relacionado | [Trazabilidad de riesgos](trazabilidad_riesgos.md) |

---

## 1. Propósito y alcance

Este documento reúne los requerimientos del MVP de Demanda360 y muestra, para cada uno, de dónde sale, cómo se comprueba y en qué estado se encuentra. Su objetivo es que el equipo y el docente puedan ver con claridad qué está integrado en el código, qué se ha revisado y qué falta por verificar.

El alcance corresponde al plan del MVP: registro de productos, conteos, atenciones, entradas y ajustes; cálculo del saldo y del estado de cada producto; alerta de stock crítico con n8n; indicadores (KPI) y, como segunda etapa (P1), sugerencias de compra y pedidos con aprobación del propietario.

Este documento **no** demuestra que el sistema funcione. Separa lo que está integrado en el repositorio de lo que se ha verificado, y deja indicado lo que todavía necesita evidencia.

## 2. Fuentes

| Código | Fuente | Fecha o versión | Uso en este documento |
| --- | --- | --- | --- |
| PLAN | Demanda360 — Plan del MVP (versión aterrizada) | 7 nov 2026 | Alcance, prioridades, reglas de cálculo, controles y criterios de aceptación (secciones 1 a 9) |
| CONTRATO | `docs/api/contrato.md` | Decisiones aprobadas el 8 nov 2026 | Rutas, reglas vigentes y estado de implementación declarado |
| README | `README.md` del repositorio | Versión entregada el 8 nov 2026 | Pantallas, pruebas, seguridad implementada y dueños de carpetas |
| AS-IS | BPMN AS-IS v3 (PR #4) | 8 nov 2026 | Proceso actual y fricciones MEDITA |
| TO-BE | BPMN TO-BE v3 y sus vistas V1 a V4 | 8 nov 2026 | Actividades del proceso propuesto |
| JUST | `docs/bpmn/justificacion_to_be.md` | 8 nov 2026 | Relación entre fricciones y cambios |
| TALLER | Taller de Seguridad: Aplicación de ISO 27001 e ISO 27002 en Demanda360 | 4 nov 2026 | Riesgos, RTO y RPO propuestos, medidas de seguridad y ética |
| QUINTANA | Respuestas confirmadas por Quintana | 8 nov 2026 | Reglas de KPI, catálogos, cliente que regresa, ajustes, SIN_CONTEO y pedidos P1 |

Cuando dos fuentes no coinciden, se usa la más reciente (por lo general, CONTRATO) y la diferencia queda anotada en la [sección 9](#9-diferencias-entre-documentos).

Abreviaturas usadas en la columna «Fuente»: «CONTRATO E1» y «CONTRATO E3» son las precisiones de las etapas 1 y 3; «CONTRATO P1» son las precisiones de pedidos; «CONTRATO n8n» es la tabla de la alerta de stock crítico. «TO-BE V1» a «TO-BE V4» son las vistas ampliadas del TO-BE v3.

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
| Integrado | El CONTRATO o el README lo describen como implementado y el código está en `main` (PR #5 y #6). No significa que funcione correctamente. |
| Sin confirmar | Está documentado, pero no hay información de que el código o el artefacto exista. |
| Diseñado | Solo aparece en el plan o en el BPMN. |

### 3.3 Estado de verificación

| Valor | Significado |
| --- | --- |
| Mocks | Revisado visualmente por el Rol 4 en Live Server con datos simulados (`frontend/static/mock/`). No prueba el backend. |
| Reportado | Lo afirma Quintana o el CONTRATO, pero el Rol 4 no tiene evidencia propia. |
| Prueba declarada | El CONTRATO o el README nombran una prueba automática; su resultado no ha sido revisado por el Rol 4. |
| Pendiente | No hay ninguna verificación. |
| Probado con backend real | Hay evidencia propia contra PostgreSQL. **A la fecha, ningún requerimiento tiene este estado.** |

### 3.4 Evidencias disponibles

La columna «Evidencia» de las matrices usa estos códigos. Solo se listan evidencias que existen hoy. La columna «Ubicación» distingue lo que está en la carpeta compartida del proyecto de lo que está registrado en GitHub.

| Código | Evidencia | Ubicación | Qué demuestra y qué no |
| --- | --- | --- | --- |
| EV-01 | Captura `dashboard_preview.png` | Carpeta compartida del proyecto (`prototipo/`). No se ha comprobado si está en GitHub. | Dashboard con mocks. No prueba el backend. |
| EV-02 | Captura `dashboard_preview_saldo_null.png` | Carpeta compartida del proyecto (`prototipo/`). No se ha comprobado si está en GitHub. | Visualización de «Sin conteo» con un mock modificado temporalmente. |
| EV-03 | Captura `registro_preview_trabajador.png` | Carpeta compartida del proyecto (`prototipo/`). No se ha comprobado si está en GitHub. | Registro con rol trabajador, con mocks. |
| EV-04 | Captura `registro_preview_propietario.png` | Carpeta compartida del proyecto (`prototipo/`). No se ha comprobado si está en GitHub. | Registro con rol propietario, con mocks. |
| EV-05 | Captura `registro_preview_ajuste.png` | Carpeta compartida del proyecto (`prototipo/`). No se ha comprobado si está en GitHub. | Formulario de ajuste con mocks. |
| EV-06 | Captura `registro_preview_error_409_simulado.png` | Carpeta compartida del proyecto (`prototipo/`). No se ha comprobado si está en GitHub. | Mensaje de error 409 simulado en pantalla. No es una respuesta real del backend. |
| EV-07 | Revisión visual del Rol 4 (8 nov 2026) de Dashboard, Registro y Planificación con ambos roles; consola de Planificación sin errores durante la carga | Sin registro guardado | No hay captura de esta revisión. |
| EV-08 | Reporte de Quintana: con cobertura de 7 días, el sugerido total pasa de 54 a 24 unidades | Sin registro guardado | Sin captura. Es un dato reportado. |
| EV-09 | PR #5 (Dashboard y Registro con la API real) y PR #6 (pedidos P1 y Planificación) | GitHub. Fusionados en `main`, según lo informado por el equipo. | Demuestran integración del código, no su funcionamiento. |
| EV-10 | PR #4 (BPMN AS-IS v3) y PR #7 (BPMN TO-BE v3, SVG, vistas y justificación) | GitHub. Ambos PR están fusionados en `main`. El PR #7 se fusionó mediante el commit `68b616b`. | Evidencia documental de los BPMN integrados en `main`. No demuestra el funcionamiento del MVP. |
| EV-11 | `backend/tests/test_kpi_demo.py`, nombrado en CONTRATO y README | Repositorio, según el CONTRATO y el README | Prueba declarada; no se ha revisado su resultado. |

> Las capturas EV-01 a EV-06 se tomaron del prototipo antes de que Quintana pasara la lógica a los archivos compartidos de `frontend/static/js/`, así que pueden no reflejar exactamente la versión integrada. Si se suben al repositorio, por ejemplo junto con el prototipo o en una carpeta de evidencias, esta tabla debe actualizarse con la ruta comprobada.

**Faltan evidencias propias** del funcionamiento de los controles del backend (códigos 401, 403, 409, CSRF, auditoría), de la alerta con n8n, de la restauración de respaldos y de los procedimientos operativos (folios manuales, verificación de contactos).

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
| RF-01 | Iniciar sesión | El usuario ingresa con su usuario y contraseña en `/login`. | P0 | Ambos | PLAN §4; CONTRATO; README | Con credenciales válidas entra a la aplicación. Una ruta `/api` sin sesión responde 401 `NO_AUTENTICADO`. | Integrado | Pendiente (los prototipos con mocks no tienen inicio de sesión) | — |
| RF-02 | Mostrar acciones según el rol | La pantalla oculta al trabajador las opciones reservadas al propietario. | P0 | Ambos | CONTRATO E1; PLAN §9 | Los elementos con clase `solo-propietario` no se muestran con rol trabajador. Ocultarlos es solo una comodidad visual: el control real es RNF-03. | Integrado | Mocks (selector «Ver como») | EV-03, EV-04, EV-07 |
| RF-03 | Crear producto | El propietario registra una referencia nueva; categoría, proveedor y unidad se eligen de las listas de `GET /api/catalogos`. | P0 | Propietario | PLAN §4; CONTRATO E3; QUINTANA | Producto válido → 201. SKU repetido → 409 `SKU_DUPLICADO`. Trabajador → 403 `SIN_PERMISO`. | Integrado | Mocks (formulario visible solo para el propietario). Los códigos 201, 409 y 403 están pendientes. | EV-07 |
| RF-04 | Consultar productos | Se consulta la lista de productos con su saldo y estado, y el detalle de un producto con sus últimos 10 movimientos. | P0 | Ambos | PLAN §4; CONTRATO E1 | El estado es uno de `SIN_CONTEO`, `AGOTADO`, `CRITICO`, `DATOS_INSUFICIENTES`, `BAJA_ROTACION` o `NORMAL`. Un `saldo: null` se muestra como «Sin conteo», nunca como 0. | Integrado | Mocks (de forma indirecta, en los selectores de Registro y en las tablas del Dashboard) | EV-02, EV-07 |

### 5.2 Inventario

| ID | Nombre | Descripción | Prioridad | Actor | Fuente | Criterio de aceptación | Implementación | Verificación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RF-05 | Registrar conteo físico | Se registra la cantidad contada de un producto; el formulario envía un `origen_ref`. | P0 | Ambos | CONTRATO E3; QUINTANA; TO-BE V1 | Conteo válido → 201 con `saldo_anterior` y `saldo_actual`. Cantidad negativa o no entera → 400. Reenvío con el mismo `origen_ref` → 200 con `duplicado: true`. | Integrado | Mocks | EV-03, EV-07 |
| RF-06 | Calcular el saldo | El saldo se calcula como último conteo + entradas − ventas ± ajustes posteriores. No se guarda en ninguna tabla. | P0 | Sistema | PLAN §3; CONTRATO (`02_vistas.sql`) | Con un conteo de 5 y una venta de 2, el saldo queda en 3. Sin conteo, el saldo es `null`. | Integrado | Pendiente | — |
| RF-07 | Clasificar el estado del producto | El sistema asigna el estado en este orden: Sin conteo → Agotado → Crítico → Datos insuficientes → Baja rotación → Normal. | P0 | Sistema | PLAN §3; CONTRATO E1 y E3 | Con los datos demo, la respuesta de `GET /api/productos` es idéntica a su mock. Un producto contado después del corte queda en `DATOS_INSUFICIENTES`, salvo que esté agotado o crítico. | Integrado | Mocks; Reportado (CONTRATO) | EV-01, EV-07 |
| RF-08 | Registrar entrada de mercancía | Se registra la mercancía que llega y el saldo aumenta. | P0 | Ambos | PLAN §4; CONTRATO E3; TO-BE V4 | Cantidad mayor que 0 → 201 y el saldo sube. Producto que nunca se ha contado → 409 `SIN_CONTEO`. | Integrado | Mocks (el 409 solo se simuló en pantalla) | EV-06, EV-07 |
| RF-09 | Registrar ajuste justificado | El propietario corrige el saldo con una cantidad con signo y una justificación. | P0 | Propietario | PLAN §7; CONTRATO E3; QUINTANA | Cantidad distinta de 0. Justificación de 10 a 500 caracteres. Si deja el saldo negativo → 409 `STOCK_INSUFICIENTE`. Producto sin conteo → 409 `SIN_CONTEO`. Trabajador → 403. | Integrado | Mocks | EV-05, EV-07 |

### 5.3 Atención al cliente y alertas

| ID | Nombre | Descripción | Prioridad | Actor | Fuente | Criterio de aceptación | Implementación | Verificación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RF-10 | Registrar la atención al cliente | En un solo registro se guarda lo que pidió el cliente y lo que recibió; si recibió algo, se genera la venta. | P0 | Ambos | PLAN §4; CONTRATO; TO-BE V3 | Entregado = 0 → se guarda como demanda no atendida y el saldo no cambia. Entregado mayor que el saldo → 409 `STOCK_INSUFICIENTE` y no se guarda nada. Entrega mayor que 0 en un producto sin conteo → 409 `SIN_CONTEO`. La respuesta trae `solicitud_id`, `no_atendida` y el bloque `producto`. | Integrado | Mocks | EV-03, EV-07 |
| RF-11 | Relacionar al cliente que regresa | Cuando el cliente vuelve por lo que faltó, se elige su atención en la lista `faltantes_pendientes` y la venta se envía con `solicitud_previa_id`. | P0 | Ambos | CONTRATO E3 y decisión 2; QUINTANA | Misma referencia, enlazada a la atención original y con cantidad menor o igual al faltante; si no, 400. El regreso no suma a lo solicitado ni a lo no atendido (KPI 2), pero sus unidades sí cuentan como vendidas. | Integrado | Pendiente. El selector de faltantes no se ha probado; en el prototipo anterior solo se probó escribir a mano el número de la atención. | — |
| RF-12 | Generar la alerta de stock crítico | Cuando una venta hace que el saldo cruce el umbral, se crea una alerta. | P0 | Sistema | PLAN §3 y §5; CONTRATO n8n | Saldo antes > umbral ≥ saldo después → fila `PENDIENTE` en `alertas_enviadas` con `evento_id` único, en la misma transacción. Una segunda venta bajo el umbral no repite la alerta. | Integrado | Pendiente | — |
| RF-13 | Enviar el correo de stock crítico | n8n recibe el evento con su token y envía el correo al equipo. | P0 | n8n | PLAN §5; CONTRATO n8n | Llega el correo y la alerta queda `ENVIADA`. Token inválido → 403. Si falla el envío, n8n responde 502 y la alerta queda `FALLIDA`. El correo incluye el `evento_id`. | Parte de Flask integrada; flujo de n8n sin confirmar | Pendiente (Rol 2) | — |
| RF-14 | Reintentar alertas fallidas | El comando `flask reintentar-alertas` reenvía las alertas que no se enviaron. | P0 | Sistema | PLAN §5; CONTRATO n8n; README | Con n8n apagado, la venta se guarda y la alerta queda `FALLIDA`; al encender n8n y correr el comando, pasa a `ENVIADA`. Reenvía también las `PENDIENTE` de más de un minuto, con el mismo `evento_id` y máximo 3 intentos. Una `ENVIADA` nunca se reenvía. | Integrado | Pendiente | — |

### 5.4 Consulta y auditoría

| ID | Nombre | Descripción | Prioridad | Actor | Fuente | Criterio de aceptación | Implementación | Verificación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RF-15 | Mostrar el Dashboard | Se muestran los KPI 1 a 3 con numerador, denominador y `detalle`, y la lista de productos críticos o agotados. | P0 | Ambos | CONTRATO; QUINTANA; TO-BE V1 | Con los datos demo y corte 2026-09-30: KPI 1 = 27,3 %, KPI 2 = 8,6 %, KPI 3 = 50 %. Un `corte` con formato inválido o una fecha futura → 400. Se ve la etiqueta «Datos simulados». | Integrado | Mocks (tres KPI, once referencias y cinco productos críticos o agotados); Prueba declarada | EV-01, EV-07, EV-11 |
| RF-16 | Consultar rotación y cobertura | Por cada producto se consultan las unidades vendidas y no atendidas en 30 días, la cobertura en días y el plazo del proveedor. | P0 | Ambos | PLAN §4; CONTRATO | Responde los campos del mock de rotación; los productos con datos insuficientes traen `dias_con_registro`. | Integrado. **Solo API**: ni el CONTRATO ni el README la asocian a una pantalla. | Pendiente | — |
| RF-17 | Registrar la auditoría | Cada operación deja una fila en la tabla `auditoria`, dentro de la misma transacción. | P0 | Sistema | PLAN §7 y §9; CONTRATO P1 | Cada operación registrada deja su fila. En pedidos se registran `PEDIDO_CREADO`, `PEDIDO_APROBADO`, `PEDIDO_ENVIADO`, `PEDIDO_CONFIRMADO`, `PEDIDO_CANCELADO` y `PEDIDO_REINTENTO`. | Integrado | Pendiente | — |
| RF-18 | Consultar la auditoría | El propietario consulta las últimas operaciones registradas. | P0 | Propietario | PLAN §4 y §7 | `GET /api/auditoria` devuelve las últimas operaciones. Trabajador → 403. | Integrado. **Solo API**: ni el CONTRATO ni el README la asocian a una pantalla. | Pendiente | — |

### 5.5 Planificación de pedidos (P1)

| ID | Nombre | Descripción | Prioridad | Actor | Fuente | Criterio de aceptación | Implementación | Verificación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RF-19 | Calcular cantidades sugeridas | Se calcula cuánto pedir de cada producto con una fórmula visible y una cobertura ajustable entre 1 y 90 días (14 por defecto). | P1 | Propietario | PLAN §3; CONTRATO P1; TO-BE V1 | Con 14 días: laca catalizada alto brillo = 24 y total = 54. Cada línea trae `formula`. Con datos insuficientes, el sugerido es `null` y se define a mano. | Integrado | Mocks (14 días; «Recalcular» no cambia con el mock porque está fijo en 14 días); Prueba declarada (54); Reportado (7 días → 24) | EV-07, EV-08, EV-11 |
| RF-20 | Crear el borrador del pedido | Se crea un pedido en estado `BORRADOR`; el servidor calcula la `cantidad_sugerida` de cada línea. | P1 | API: ambos roles (CONTRATO). Pantalla: solo el propietario, según la revisión visual. | CONTRATO P1; PLAN §4; TO-BE V1 | Crea un `BORRADOR` con 1 a 50 líneas y sin productos repetidos; si no, 400. | Integrado | Mocks (visual). **Pendiente de confirmar con Quintana** qué rol debe poder crear borradores ([pregunta 1](#10-preguntas-para-quintana)). | EV-07 |
| RF-21 | Aprobar el pedido | El propietario pasa el pedido de borrador a aprobado. | P1 | Propietario | CONTRATO P1; TO-BE V1 | `BORRADOR → APROBADO` y queda registrado quién aprobó. Trabajador → 403 `SIN_PERMISO`. | Integrado | Mocks (solo visual y permisos por rol). Verificación funcional pendiente. | EV-07 |
| RF-22 | Registrar el envío y la confirmación | Se registra que el pedido se envió al proveedor y, después, su confirmación. | P1 | Propietario | CONTRATO P1; TO-BE V2 | `APROBADO → ENVIADO` registra `fecha_envio`. `ENVIADO → CONFIRMADO` registra `fecha_respuesta` y `fecha_entrega_estimada`. Cualquier otro salto → 409 `TRANSICION_INVALIDA`. Confirmar no suma inventario. | Integrado | Mocks (solo visual y permisos por rol). Verificación funcional pendiente. | EV-07 |
| RF-23 | Cancelar el pedido | El propietario cancela un pedido indicando el motivo. | P1 | Propietario | CONTRATO P1; TO-BE V2 | Se puede cancelar desde `BORRADOR`, `APROBADO` o `ENVIADO`, con un motivo de 5 a 300 caracteres. | Integrado | Pendiente | — |
| RF-24 | Reintentar con otro proveedor | Al cancelar, el propietario puede crear un nuevo intento del mismo pedido con un proveedor distinto. | P1 | Propietario | CONTRATO P1 y decisión 3; TO-BE V2 | Con `reintentar_con_proveedor_id` se crea un pedido nuevo con las mismas líneas, `numero_intento + 1`, `pedido_anterior_id` y estado `APROBADO`. Un pedido se reintenta una sola vez. | Integrado | Pendiente | — |
| RF-25 | Consultar pedidos y tiempo de espera | Se consulta la lista de pedidos y, en los enviados sin respuesta, cuántas horas llevan esperando. | P1 | Ambos | CONTRATO P1; nota de TO-BE V2 | Devuelve los últimos 100 pedidos, del más nuevo al más viejo. Los `ENVIADO` sin respuesta traen `horas_esperando` (no es el plazo de entrega). | Integrado | Mocks (lista de pedidos y estados) | EV-07 |

### 5.6 Analítica (P1)

| ID | Nombre | Descripción | Prioridad | Actor | Fuente | Criterio de aceptación | Implementación | Verificación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RF-26 | Calcular el KPI 4 | Se calcula el tiempo promedio, en horas, que tarda un proveedor en confirmar. | P1 | Sistema | PLAN §6; CONTRATO | Promedio de (respuesta − envío) de los pedidos con ambas fechas en el período. Los pedidos sin respuesta no se promedian; se cuentan aparte. | Integrado (vista SQL) | Pendiente | — |
| RF-27 | Calcular el KPI 5 | Se calcula el porcentaje de pedidos confirmados con el primer proveedor. | P1 | Sistema | PLAN §6; CONTRATO | Pedidos confirmados en el intento 1 / pedidos confirmados, contando cada cadena de reintentos una sola vez. | Integrado (vista SQL) | Pendiente | — |
| RF-28 | Exportar las vistas a CSV | El script `analytics/exportar_csv.sh` exporta las vistas para Power BI. | P1 | Sistema | PLAN §6; README | Los CSV quedan en `analytics/datos_demo/` y cada uno lleva la columna `origen_datos`. | Sin confirmar | Pendiente | — |
| RF-29 | Visualizar los KPI en Power BI | Un tablero de cinco páginas muestra los cinco KPI a partir de los CSV. | P1 | Propietario | PLAN §6 | Muestra los cinco KPI con la marca «Datos simulados» y la hoja de verificación cuadra con las vistas. | Sin confirmar | Pendiente (Rol 3) | — |

## 6. Requerimientos no funcionales

| ID | Nombre | Descripción | Categoría | Prioridad | Fuente | Criterio de aceptación | Implementación | Verificación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RNF-01 | Autenticación con sesión | La sesión usa Flask-Login con cookie `HttpOnly` y vence a las 8 horas. | Seguridad | P0 | PLAN §7 (control 3); README; CONTRATO E3 | Una ruta sin sesión responde 401. En un `POST` sin sesión, el 401 aparece antes del chequeo de CSRF. | Integrado | Reportado (README) | — |
| RNF-02 | Contraseñas con hash | Las contraseñas se guardan con hash (scrypt), nunca en texto plano. | Seguridad | P0 | PLAN §7 (control 4); README | La consulta a la tabla `usuarios` muestra solo hashes. | Integrado | Reportado (README) | — |
| RNF-03 | Permisos verificados en el backend | Cada ruta verifica el rol en el servidor. Ocultar un botón no cuenta como control. | Seguridad | P0 | PLAN §4 y §7 (controles 5 y 6); CONTRATO | El trabajador recibe 403 `SIN_PERMISO` al crear un producto, ajustar, consultar sugeridos, aprobar, cambiar el estado de un pedido o consultar la auditoría. | Integrado | Pendiente | — |
| RNF-04 | Protección CSRF | Todo `POST` envía la cabecera `X-CSRFToken`. | Seguridad | P0 | PLAN §4; CONTRATO E1 | Token ausente o inválido → 400 `VALIDACION` con `campos: {"csrf": "invalido"}`. | Integrado | Pendiente | — |
| RNF-05 | Validación de datos | Se valida el SKU único, que las cantidades sean enteras y que la unidad esté dentro de la lista. | Integridad | P0 | PLAN §7 (controles 1 y 2) | SKU repetido → 409. Cantidad inválida → 400. | Integrado | Pendiente | — |
| RNF-06 | Saldo consistente | La venta se registra en una transacción que bloquea la fila del producto (`SELECT … FOR UPDATE`). | Integridad | P0 | PLAN §3 | Una venta mayor que el saldo responde 409 y no guarda nada; el saldo nunca queda negativo. | Integrado | Pendiente | — |
| RNF-07 | Sin registros duplicados | Cada formulario genera un `origen_ref` para evitar que un reenvío cree dos registros. | Integridad | P0 | PLAN §4; CONTRATO E3 y P1 | Reenvío → 200 con `duplicado: true`. Un `origen_ref` usado en otro tipo de registro → 409 `ORIGEN_REF_EN_USO`. En pedidos, que no tienen `origen_ref`, el botón se bloquea mientras guarda. | Integrado | Pendiente | — |
| RNF-08 | Manejo uniforme de errores | Todos los errores usan el formato `{"error": {"codigo", "mensaje", "campos"}}` y nunca muestran trazas. | Seguridad | P0 | PLAN §4; CONTRATO E1 | El 500 trae `error.referencia` igual a la cabecera `X-Request-ID`. Un método no permitido → 405 `METODO_NO_PERMITIDO`. | Integrado | Pendiente | — |
| RNF-09 | Movimientos inmutables y bitácora | Los movimientos no se borran ni se editan; las correcciones se hacen con ajustes. La auditoría es de solo inserción. | Integridad | P0 | PLAN §7 (controles 7 y 8); README | Un movimiento existente no se puede borrar ni modificar. | Integrado | Reportado (README) | — |
| RNF-10 | Continuidad de la venta ante fallas de n8n | Una falla en el envío de la alerta no afecta la venta ya registrada. | Disponibilidad | P0 | PLAN §5; CONTRATO n8n | Si n8n está apagado, responde 502 o no contesta en 10 s, la venta queda guardada y la alerta queda `FALLIDA`. | Integrado | Pendiente | — |
| RNF-11 | Secretos fuera del repositorio | Las credenciales viven solo en `.env`. | Seguridad | P0 | PLAN §7 (control 9); README | `.env` está fuera de Git y `.env.example` no tiene valores. | Integrado | Pendiente | — |
| RNF-12 | Servicios no expuestos a la red | Los servicios solo escuchan en el equipo local y n8n se protege con token. | Seguridad | P0 | PLAN §2 y §7; README | Puertos atados a `127.0.0.1`; PostgreSQL no responde desde otro equipo de la red; el webhook rechaza un token inválido; la app corre sin privilegios de root en el contenedor. | Integrado | Pendiente (Rol 2) | — |
| RNF-13 | Respaldo y restauración probada | Se hace un respaldo con `pg_dump` fuera del repositorio y se comprueba que se puede restaurar. | Disponibilidad | P0 | PLAN §7; TALLER §9 a §11 | Se restaura en una base de prueba aislada (`demanda360_restore`), sin afectar la base de trabajo del equipo; se comparan los conteos de las tablas y el saldo de tres referencias, y se anota la duración. El RTO de 4 horas y el RPO de 1 hora son **objetivos propuestos en el TALLER, sujetos a un simulacro**; no son resultados. | Sin confirmar | Pendiente | — |
| RNF-14 | Minimización de datos personales | El sistema no guarda datos de clientes; el contacto del proveedor es opcional (Ley 1581 de 2012). | Privacidad | P0 | PLAN §5 y §7 (control 11); TALLER §13 | No hay campos de datos de clientes. El correo de alerta lleva solo SKU, nombre, saldo, umbral y plazo. | Integrado | Pendiente | — |
| RNF-15 | Datos rotulados y reglas transparentes | La interfaz indica el origen de los datos que muestra y cada sugerencia explica su cálculo. | Ética y transparencia | P0 | PLAN §1 y §7; CONTRATO | La etiqueta «Datos simulados» se muestra en el modo con mocks y cuando las respuestas traen `origen_datos: SIMULADO`. Con datos reales, la interfaz no los identifica como simulados. Cada sugerido trae su `formula`. | Integrado (rotulado de datos simulados) | Mocks. El comportamiento con datos reales está pendiente de verificación, porque la demo solo usa datos simulados. | EV-01, EV-07 |
| RNF-16 | Formularios que conservan lo escrito | Ante un error, el formulario muestra el mensaje de la API sin borrar lo que el usuario escribió. | Usabilidad | P0 | PLAN §9; CONTRATO | Se muestra el mensaje del 400 o del 409 y se conservan los datos. La justificación del ajuste exige 10 caracteres también en la pantalla. | Integrado | Mocks (parcial: el error solo se simuló) | EV-05, EV-06 |
| RNF-17 | Lógica en un solo lugar | Las pantallas comparten el mismo JavaScript y los cálculos oficiales viven en `database/sql/02_vistas.sql`. | Mantenibilidad | P0 | CONTRATO; README | Prototipos y plantillas cargan los mismos `comun.js`, `dashboard.js`, `registro.js` y `planificacion.js`. | Integrado | Mocks (consola de Planificación sin errores) | EV-07 |
| RNF-18 | Control de versiones e integración continua | Los cambios entran a `main` solo por pull request y las pruebas corren en GitHub. | Mantenibilidad | P0 | PLAN §7 (control 12); README | Todo cambio entra por PR con una aprobación y las pruebas en verde. | Integrado según el README | Pendiente. Un PR aprobado no demuestra que la CI esté en verde: hay que revisar el resultado de cada ejecución y confirmar que la protección de `main` está activa. | EV-09, EV-10 (solo prueban que los PR existen) |
| RNF-19 | Despliegue con Docker Compose | El sistema se levanta con un solo comando. | Despliegue | P0 | PLAN §9; README | `docker compose up -d` levanta `db`, `web` y `n8n`. `GET /api/health` responde `{"estado":"ok","bd":"ok"}`. | Integrado | Pendiente | — |

**Rendimiento.** Ningún documento define una métrica de rendimiento, así que no se incluye un RNF de esa categoría. La única cifra de tiempo documentada es la espera máxima de 10 segundos de la alerta, y ya forma parte de RNF-10. Si el equipo define un valor, se agregará en una versión posterior.

## 7. Actividades manuales del TO-BE

Estas actividades aparecen en el TO-BE v3, pero se hacen fuera del sistema, así que no se convierten en requerimientos funcionales:

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

### 9.1 Resueltas por el contrato vigente

| # | Diferencia | Cómo quedó |
| --- | --- | --- |
| 1 | `GET /api/catalogos` no estaba en el plan. | El CONTRATO la define para ambos roles (`categorias`, `proveedores`, `unidades_medida`). |
| 2 | La tabla `conteos_fisicos` del plan no tiene `origen_ref`. | El CONTRATO indica que el conteo envía `origen_ref` y agrega el error `ORIGEN_REF_EN_USO`. Falta confirmar la columna en el esquema (pregunta 7). |
| 3 | `solicitud_previa_id` no estaba en la tabla `solicitudes_clientes` del plan. | El CONTRATO define `faltantes_pendientes` en `GET /api/productos/{id}` y la regla del cliente que regresa (decisión 2). |
| 4 | El plan no nombraba el código de error para productos sin conteo. | `409 SIN_CONTEO` en entradas, ajustes y ventas con entrega mayor que 0. |
| 5 | Texto de los KPI: `nota` o `detalle`. | Queda `detalle`. |
| 6 | KPI 1: 27 % o 27,3 %. | El CONTRATO y el README usan 27,3 %. El plan (§6 y §9) todavía dice 27 %. |
| 7 | Si el nuevo intento con otro proveedor necesita otra aprobación. | El reintento nace `APROBADO` por el propietario que lo pide y se permite una sola vez. |
| 8 | Formato de identificadores y prioridades del README del Rol 4 (RF01, solo P0 y P1). | Se usa RF-01 y RNF-01; lo P2 va como lista aparte. |

### 9.2 Abiertas

| # | Diferencia | Dónde se resuelve |
| --- | --- | --- |
| 1 | Crear borradores: la API acepta ambos roles, pero en la pantalla solo el propietario tiene «Guardar borrador». | Pregunta 1 |
| 2 | La tabla de 15 rutas del CONTRATO no incluye `GET /api/catalogos`, aunque el mismo documento la describe. | Pregunta 6 |
| 3 | Espera máxima de la alerta: 3 s en el plan y 10 s en el CONTRATO. Se usa la del CONTRATO. | Pregunta 10 |
| 4 | Ningún documento define una métrica de rendimiento. | Decisión del equipo |
| 5 | El TO-BE v3 y `justificacion_to_be.md` dicen que P1 no está implementado y conservan pendientes que el CONTRATO ya resolvió. | [Sección 11](#11-cambios-pendientes-en-el-to-be) |

## 10. Preguntas para Quintana

### 10.1 Afectan decisiones del MVP

1. **Borradores (RF-20):** ¿quién debe poder crear borradores, ambos roles o solo el propietario? Según la respuesta, se ajusta el CONTRATO o la pantalla.
2. **Rotación y auditoría (RF-16 y RF-18):** ¿quedan solo como API y como evidencia, o alguna pantalla debe consumirlas?
3. **KPI 4 y 5 (RF-26 y RF-27):** ¿se muestran solo en los CSV y en Power BI, o también en alguna ruta o pantalla?
4. **Umbral y contacto del proveedor:** no hay una ruta para editarlos. ¿Se confirma que su edición queda fuera del MVP? Afecta a los riesgos R4 y R6.
5. **Respaldo (RNF-13):** ¿ya existen `scripts/backup.sh` y `scripts/restore_prueba.sh`? ¿Quién los escribe y quién los ejecuta? Esto último se debe acordar también con Brayan.

### 10.2 Aclaraciones documentales o de evidencia

6. Agregar `GET /api/catalogos` a la tabla de rutas del CONTRATO. El cambio necesita la aprobación del Rol 1 y del Rol 4.
7. Confirmar que la columna `origen_ref` existe en `conteos_fisicos` dentro de `database/sql/01_schema.sql`.
8. Compartir el resultado de la CI en los PR #5 y #6 e indicar qué prueba cubre cada requerimiento.
9. Confirmar si la protección de la rama `main` está activa en el repositorio.
10. Confirmar que la espera de 10 s del CONTRATO reemplaza los 3 s del plan.

## 11. Cambios pendientes en el TO-BE

El BPMN TO-BE v3 y su justificación se deben actualizar con el contrato P1 vigente. **Estos cambios quedan registrados y no se han ejecutado.** Se harán cuando los requerimientos estén cerrados.

### 11.1 Diagrama `Demanda360_TO_BE_v3.bpmn`

1. Cambiar la leyenda de «[P1] … no está implementada» por «[P1] integrada en `main` (PR #6), pendiente de verificación funcional».
2. Quitar la nota pendiente sobre una nueva aprobación y escribir: «El reintento nace APROBADO por el propietario que lo pide y solo se permite una vez».
3. En la compuerta «¿Hay otro proveedor disponible?», agregar la condición de que el pedido no se haya reintentado antes. Si ya se reintentó, el pedido termina `CANCELADO`.
4. En la atención al cliente, agregar la salida «Producto sin conteo (409 SIN_CONTEO)» cuando la entrega es mayor que 0, y quitar la nota pendiente sobre SIN_CONTEO.
5. En la entrada de mercancía, agregar la misma salida 409 `SIN_CONTEO`.
6. Cambiar la nota del cliente que regresa por: «La atención original se escoge en la lista de faltantes pendientes».
7. En la confirmación del pedido, agregar: «Confirmar no suma inventario; la mercancía se registra al llegar» (relación con la vista 4).
8. Actualizar la nota de alertas: n8n responde 200 solo después de enviar el correo y 502 si falla; Flask espera 10 s como máximo; el reintento incluye las alertas `PENDIENTE` con más de un minuto.
9. Ajustar el carril de «Crear el borrador del pedido» cuando Quintana responda la pregunta 1.
10. Regenerar las vistas ampliadas V1 a V4 con los cambios anteriores.

### 11.2 `justificacion_to_be.md`

1. **Sección 3:** actualizar el estado. Dashboard, Registro y Planificación están integrados en `main` y se revisaron con mocks; no hay verificación propia contra PostgreSQL.
2. **Tabla de la sección 4:** actualizar la columna «Comprobado a la fecha» en las fricciones I, E y T. P1 está integrado, pero no verificado, y sus beneficios siguen siendo esperados.
3. **Sección 6:** agregar las reglas de `SIN_CONTEO` y del reintento único con otro proveedor.
4. **Sección 7:** marcar como resueltos los pendientes 1 y 2 y conservar la observación 3 (el plan solo define alertas por ventas).

## 12. Historial de cambios

| Versión | Fecha | Cambio | Autor |
| --- | --- | --- | --- |
| 1.0 | 8 nov 2026 | Primera versión: 29 RF, 19 RNF, diferencias, preguntas y cambios pendientes del TO-BE. | Jhonatan Rey (Rol 4) |
| 1.1 | 8 nov 2026 | Se distingue la ubicación de las evidencias (carpeta compartida o GitHub) y el estado de cada PR. Se precisa el rotulado de datos simulados en RNF-15. | Jhonatan Rey (Rol 4) |
