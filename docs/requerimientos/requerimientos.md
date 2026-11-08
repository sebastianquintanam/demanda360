# Requerimientos funcionales y no funcionales · Demanda360

| Campo | Valor |
| --- | --- |
| Proyecto | Demanda360 – MVP para Pinturas By-plus |
| Documento | Matriz de requerimientos funcionales (RF) y no funcionales (RNF) |
| Versión | 1.2 |
| Fecha | 8 de noviembre de 2026 |
| Elaborado por | Jhonatan Stiben Rey Velásquez (Rol 4: frontend, prototipos, BPMN y requerimientos) |
| Estado | Versión de cierre del Rol 4, actualizada con el informe de estado de Quintana (Rol 1) del 8 nov 2026. Los pendientes reales están en la [sección 9.2](#92-pendientes-reales). |
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
| INFORME | `estado_demanda360_8nov.md`, informe de estado de Quintana (Rol 1) | 8 nov 2026 | Estado de los PR, pruebas reportadas, KPI 4 y 5, CSV, criterios de demostración y respuestas a las diez preguntas de la versión 1.1 (su sección 5) |

Cuando dos fuentes no coinciden, se usa la más reciente (por lo general, CONTRATO) y la diferencia queda anotada en la [sección 9](#9-diferencias-entre-documentos).

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
| Integrado | El CONTRATO, el README o el INFORME lo describen como implementado y el código está en `main`. Según el INFORME, los PR #1 a #10 están fusionados en `main`, y Dashboard, Registro y Planificación consumen la API real. No significa que funcione correctamente. |
| Pendiente | El INFORME indica que el artefacto todavía no existe o no se ha entregado. |
| Sin confirmar | Está documentado, pero no hay información de que el código o el artefacto exista. |
| Diseñado | Solo aparece en el plan o en el BPMN. |

### 3.3 Estado de verificación

| Valor | Significado |
| --- | --- |
| Mocks | Revisado visualmente por el Rol 4 en Live Server con datos simulados (`frontend/static/mock/`). No prueba el backend. |
| Reportado | Lo afirma Quintana o el CONTRATO, pero el Rol 4 no tiene evidencia propia. |
| Prueba reportada | Quintana informa que ejecutó una prueba concreta contra PostgreSQL o n8n y que fue satisfactoria. El Rol 4 no tiene el registro de la ejecución (log de CI, capturas o salida de consola). |
| Prueba declarada | El CONTRATO o el README nombran una prueba automática; su resultado no ha sido revisado por el Rol 4. |
| Pendiente | No hay ninguna verificación. |
| Probado con backend real | Hay evidencia propia contra PostgreSQL. **A la fecha, ningún requerimiento tiene este estado.** |

> **Sobre las 150 pruebas automáticas.** El INFORME reporta 150 pruebas automáticas satisfactorias con PostgreSQL (EV-13). Como el Rol 4 no tiene el registro de la CI ni de la ejecución, y tampoco la relación entre cada prueba y cada requerimiento, este dato no cambia por sí solo la verificación de ningún RF o RNF. Solo se marca «Prueba reportada» donde el INFORME describe una prueba concreta: la prueba real de la alerta con n8n (EV-14). Estas pruebas las reporta el Rol 1; el Rol 4 no las ejecutó.

### 3.4 Evidencias disponibles

La columna «Evidencia» de las matrices usa estos códigos. Solo se listan evidencias que existen hoy. La columna «Ubicación» distingue lo que está en la carpeta compartida del proyecto de lo que está registrado en GitHub. La columna «Tipo» separa la evidencia propia del Rol 4, la evidencia documental y lo que solo está reportado en el INFORME.

| Código | Evidencia | Tipo | Ubicación | Qué demuestra y qué no |
| --- | --- | --- | --- | --- |
| EV-01 | Captura `dashboard_preview.png` | Propia (mocks) | Carpeta compartida del proyecto (`prototipo/`). No se ha comprobado si está en GitHub. | Dashboard con mocks. No prueba el backend. |
| EV-02 | Captura `dashboard_preview_saldo_null.png` | Propia (mocks) | Carpeta compartida del proyecto (`prototipo/`). No se ha comprobado si está en GitHub. | Visualización de «Sin conteo» con un mock modificado temporalmente. |
| EV-03 | Captura `registro_preview_trabajador.png` | Propia (mocks) | Carpeta compartida del proyecto (`prototipo/`). No se ha comprobado si está en GitHub. | Registro con rol trabajador, con mocks. |
| EV-04 | Captura `registro_preview_propietario.png` | Propia (mocks) | Carpeta compartida del proyecto (`prototipo/`). No se ha comprobado si está en GitHub. | Registro con rol propietario, con mocks. |
| EV-05 | Captura `registro_preview_ajuste.png` | Propia (mocks) | Carpeta compartida del proyecto (`prototipo/`). No se ha comprobado si está en GitHub. | Formulario de ajuste con mocks. |
| EV-06 | Captura `registro_preview_error_409_simulado.png` | Propia (mocks) | Carpeta compartida del proyecto (`prototipo/`). No se ha comprobado si está en GitHub. | Mensaje de error 409 simulado en pantalla. No es una respuesta real del backend. |
| EV-07 | Revisión visual del Rol 4 (8 nov 2026) de Dashboard, Registro y Planificación con ambos roles; consola de Planificación sin errores durante la carga | Propia (mocks) | Sin registro guardado | No hay captura de esta revisión. |
| EV-08 | Reporte de Quintana: con cobertura de 7 días, el sugerido total pasa de 54 a 24 unidades | Reportada | Sin registro guardado | Sin captura. Es un dato reportado. |
| EV-09 | PR #1 a #10 fusionados en `main`; entre ellos, PR #5 (Dashboard y Registro con la API real) y PR #6 (pedidos P1 y Planificación) | Reportada (INFORME) | GitHub. El Rol 4 no ha revisado el estado de cada PR de forma individual. | Demuestran integración del código, no su funcionamiento. |
| EV-10 | PR #4 (BPMN AS-IS v3), PR #7 (BPMN TO-BE v3, histórico) y PR #10 (BPMN TO-BE v4, SVG, cuatro vistas y `justificacion_to_be_v4.md`) | Documental | GitHub (`main`, según el INFORME) y carpeta compartida del proyecto (`docs/bpmn/`). | El Rol 4 revisó el contenido de los archivos v4 de la carpeta compartida y confirmó los cambios de la [sección 11](#11-cierre-de-los-cambios-del-to-be). Es evidencia del modelo, no del funcionamiento del sistema. |
| EV-11 | `backend/tests/test_kpi_demo.py`, nombrado en CONTRATO y README | Declarada | Repositorio, según el CONTRATO y el README | Prueba declarada; no se ha revisado su resultado. |
| EV-12 | Informe `estado_demanda360_8nov.md` de Quintana | Reportada | Documento compartido por Quintana con el equipo; su ruta en GitHub no se ha comprobado. | Fuente de los datos EV-13 a EV-16 y de las respuestas de la sección 10. |
| EV-13 | 150 pruebas automáticas satisfactorias con PostgreSQL | Reportada (INFORME) | Sin registro de CI ni de ejecución revisado por el Rol 4 | Indica que existe una batería de pruebas del backend. No se puede asociar a requerimientos concretos ni se considera verificada. |
| EV-14 | Prueba real de n8n: venta guardada, alerta `FALLIDA`, reintento, alerta `ENVIADA` y correo recibido | Reportada (INFORME) | Sin capturas ni registro revisados por el Rol 4 | Respalda RF-12, RF-13 (en parte), RF-14 y RNF-10 como «Prueba reportada». No se reporta el caso de token inválido (403). |
| EV-15 | CSV de los cinco KPI | Reportada (INFORME) | Ubicación no comprobada por el Rol 4; no se revisó su contenido | Indica que la exportación existe. No se ha comprobado la columna `origen_datos`. |
| EV-16 | KPI 4 = 4,7 horas y KPI 5 = 66,7 % con los datos de demostración | Reportada (INFORME) | Sin captura | Valores calculados con datos simulados. No son resultados del negocio. |

> Las capturas EV-01 a EV-06 se tomaron del prototipo antes de que Quintana pasara la lógica a los archivos compartidos de `frontend/static/js/`, así que pueden no reflejar exactamente la versión integrada. Si se suben al repositorio, por ejemplo junto con el prototipo o en una carpeta de evidencias, esta tabla debe actualizarse con la ruta comprobada.

**Faltan evidencias propias** del funcionamiento de los controles del backend (códigos 401, 403, 409, CSRF, auditoría) y de los procedimientos operativos (folios manuales, verificación de contactos). La alerta con n8n solo tiene la prueba reportada en EV-14. El respaldo y la restauración no tienen evidencia porque, al corte del INFORME, sus scripts y pruebas siguen pendientes. Las evidencias de seguridad todavía deben archivarse.

### 3.5 Criterios de demostración

Según el INFORME, de los **13 criterios de demostración**, 9 están completos, 2 están parciales y 2 están pendientes. Es un estado reportado por el Rol 1: no significa que haya 11 criterios terminados ni que el Rol 4 los haya verificado. El detalle de cada criterio está en el INFORME.

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
| RF-12 | Generar la alerta de stock crítico | Cuando una venta hace que el saldo cruce el umbral, se crea una alerta. | P0 | Sistema | PLAN §3 y §5; CONTRATO n8n | Saldo antes > umbral ≥ saldo después → fila `PENDIENTE` en `alertas_enviadas` con `evento_id` único, en la misma transacción. Una segunda venta bajo el umbral no repite la alerta. | Integrado | Prueba reportada (prueba real de n8n). Falta comprobar que una segunda venta bajo el umbral no repite la alerta. | EV-14 |
| RF-13 | Enviar el correo de stock crítico | n8n recibe el evento con su token y envía el correo al equipo. | P0 | n8n | PLAN §5; CONTRATO n8n | Llega el correo y la alerta queda `ENVIADA`. Token inválido → 403. Si falla el envío, n8n responde 502 y la alerta queda `FALLIDA`. El correo incluye el `evento_id`. | Integrado (Flask y flujo de n8n, según el INFORME) | Prueba reportada (parcial): alerta `ENVIADA` y correo recibido. Sin reporte del 403 con token inválido. | EV-14 |
| RF-14 | Reintentar alertas fallidas | El comando `flask reintentar-alertas` reenvía las alertas que no se enviaron. | P0 | Sistema | PLAN §5; CONTRATO n8n; README | Con n8n apagado, la venta se guarda y la alerta queda `FALLIDA`; al encender n8n y correr el comando, pasa a `ENVIADA`. Reenvía también las `PENDIENTE` de más de un minuto, con el mismo `evento_id` y máximo 3 intentos. Una `ENVIADA` nunca se reenvía. | Integrado | Prueba reportada (parcial): una alerta `FALLIDA` pasó a `ENVIADA` después del reintento. Sin reporte de las `PENDIENTE` de más de un minuto ni del límite de 3 intentos. | EV-14 |

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
| RF-20 | Crear el borrador del pedido | Se crea un pedido en estado `BORRADOR`; el servidor calcula la `cantidad_sugerida` de cada línea. | P1 | API: ambos roles. Pantalla Planificación: solo el propietario (decisión del MVP, [sección 10](#10-respuestas-y-decisiones-de-quintana)). | CONTRATO P1; PLAN §4; TO-BE V1 | Crea un `BORRADOR` con 1 a 50 líneas y sin productos repetidos; si no, 400. | Integrado | Mocks (visual). La diferencia entre API y pantalla queda aceptada como decisión del MVP (decisión 1) y no requiere cambios en el código. La creación por API con rol trabajador no tiene verificación propia. | EV-07 |
| RF-21 | Aprobar el pedido | El propietario pasa el pedido de borrador a aprobado. | P1 | Propietario | CONTRATO P1; TO-BE V1 | `BORRADOR → APROBADO` y queda registrado quién aprobó. Trabajador → 403 `SIN_PERMISO`. | Integrado | Mocks (solo visual y permisos por rol). Verificación funcional pendiente. | EV-07 |
| RF-22 | Registrar el envío y la confirmación | Se registra que el pedido se envió al proveedor y, después, su confirmación. | P1 | Propietario | CONTRATO P1; TO-BE V2 | `APROBADO → ENVIADO` registra `fecha_envio`. `ENVIADO → CONFIRMADO` registra `fecha_respuesta` y `fecha_entrega_estimada`. Cualquier otro salto → 409 `TRANSICION_INVALIDA`. Confirmar no suma inventario. | Integrado | Mocks (solo visual y permisos por rol). Verificación funcional pendiente. | EV-07 |
| RF-23 | Cancelar el pedido | El propietario cancela un pedido indicando el motivo. | P1 | Propietario | CONTRATO P1; TO-BE V2 | Se puede cancelar desde `BORRADOR`, `APROBADO` o `ENVIADO`, con un motivo de 5 a 300 caracteres. | Integrado | Pendiente | — |
| RF-24 | Reintentar con otro proveedor | Al cancelar, el propietario puede crear un nuevo intento del mismo pedido con un proveedor distinto. | P1 | Propietario | CONTRATO P1 y decisión 3; TO-BE V2 | Con `reintentar_con_proveedor_id` se crea un pedido nuevo con las mismas líneas, `numero_intento + 1`, `pedido_anterior_id` y estado `APROBADO`. Un pedido se reintenta una sola vez. | Integrado | Pendiente | — |
| RF-25 | Consultar pedidos y tiempo de espera | Se consulta la lista de pedidos y, en los enviados sin respuesta, cuántas horas llevan esperando. | P1 | Ambos | CONTRATO P1; nota de TO-BE V2 | Devuelve los últimos 100 pedidos, del más nuevo al más viejo. Los `ENVIADO` sin respuesta traen `horas_esperando` (no es el plazo de entrega). | Integrado | Mocks (lista de pedidos y estados) | EV-07 |

### 5.6 Analítica (P1)

| ID | Nombre | Descripción | Prioridad | Actor | Fuente | Criterio de aceptación | Implementación | Verificación | Evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RF-26 | Calcular el KPI 4 | Se calcula el tiempo promedio, en horas, que tarda un proveedor en confirmar. | P1 | Sistema | PLAN §6; CONTRATO | Promedio de (respuesta − envío) de los pedidos con ambas fechas en el período. Los pedidos sin respuesta no se promedian; se cuentan aparte. | Integrado (vista SQL) | Reportado: 4,7 horas con los datos de demostración | EV-16 |
| RF-27 | Calcular el KPI 5 | Se calcula el porcentaje de pedidos confirmados con el primer proveedor. | P1 | Sistema | PLAN §6; CONTRATO | Pedidos confirmados en el intento 1 / pedidos confirmados, contando cada cadena de reintentos una sola vez. | Integrado (vista SQL) | Reportado: 66,7 % con los datos de demostración | EV-16 |
| RF-28 | Exportar las vistas a CSV | El script `analytics/exportar_csv.sh` exporta las vistas para Power BI. | P1 | Sistema | PLAN §6; README | Los CSV quedan en `analytics/datos_demo/` y cada uno lleva la columna `origen_datos`. | Integrado según el INFORME (existen los CSV de los cinco KPI) | Reportado (existencia de los CSV). La ruta y la columna `origen_datos` no se han revisado. | EV-15 |
| RF-29 | Visualizar los KPI en Power BI | Un tablero de cinco páginas muestra los cinco KPI a partir de los CSV. | P1 | Propietario | PLAN §6 | Muestra los cinco KPI con la marca «Datos simulados» y la hoja de verificación cuadra con las vistas. | Pendiente según el INFORME | Pendiente (Rol 3). Las cinco páginas no están terminadas. | — |

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
| RNF-10 | Continuidad de la venta ante fallas de n8n | Una falla en el envío de la alerta no afecta la venta ya registrada. | Disponibilidad | P0 | PLAN §5; CONTRATO n8n | Si n8n está apagado, responde 502 o no contesta en 10 s, la venta queda guardada y la alerta queda `FALLIDA`. | Integrado | Prueba reportada: la venta quedó guardada con la alerta `FALLIDA`. El caso de espera de 10 s sin respuesta no se reporta por separado. | EV-14 |
| RNF-11 | Secretos fuera del repositorio | Las credenciales viven solo en `.env`. | Seguridad | P0 | PLAN §7 (control 9); README | `.env` está fuera de Git y `.env.example` no tiene valores. | Integrado | Pendiente | — |
| RNF-12 | Servicios no expuestos a la red | Los servicios solo escuchan en el equipo local y n8n se protege con token. | Seguridad | P0 | PLAN §2 y §7; README | Puertos atados a `127.0.0.1`; PostgreSQL no responde desde otro equipo de la red; el webhook rechaza un token inválido; la app corre sin privilegios de root en el contenedor. | Integrado | Pendiente (Rol 2). La verificación de los riesgos inherentes corresponde a Brayan. | — |
| RNF-13 | Respaldo y restauración probada | Se hace un respaldo con `pg_dump` fuera del repositorio y se comprueba que se puede restaurar. | Disponibilidad | P0 | PLAN §7; TALLER §9 a §11 | Se restaura en una base de prueba aislada (`demanda360_restore`), sin afectar la base de trabajo del equipo; se comparan los conteos de las tablas y el saldo de tres referencias, y se anota la duración. El RTO de 4 horas y el RPO de 1 hora son **objetivos propuestos en el TALLER, sujetos a un simulacro**; no son resultados. | Pendiente: los scripts de respaldo y restauración siguen pendientes al corte del INFORME | Pendiente | — |
| RNF-14 | Minimización de datos personales | El sistema no guarda datos de clientes; el contacto del proveedor es opcional (Ley 1581 de 2012). | Privacidad | P0 | PLAN §5 y §7 (control 11); TALLER §13 | No hay campos de datos de clientes. El correo de alerta lleva solo SKU, nombre, saldo, umbral y plazo. | Integrado | Pendiente | — |
| RNF-15 | Datos rotulados y reglas transparentes | La interfaz indica el origen de los datos que muestra y cada sugerencia explica su cálculo. | Ética y transparencia | P0 | PLAN §1 y §7; CONTRATO | La etiqueta «Datos simulados» se muestra en el modo con mocks y cuando las respuestas traen `origen_datos: SIMULADO`. Con datos reales, la interfaz no los identifica como simulados. Cada sugerido trae su `formula`. | Integrado (rotulado de datos simulados) | Mocks. El comportamiento con datos reales está pendiente de verificación, porque la demo solo usa datos simulados. | EV-01, EV-07 |
| RNF-16 | Formularios que conservan lo escrito | Ante un error, el formulario muestra el mensaje de la API sin borrar lo que el usuario escribió. | Usabilidad | P0 | PLAN §9; CONTRATO | Se muestra el mensaje del 400 o del 409 y se conservan los datos. La justificación del ajuste exige 10 caracteres también en la pantalla. | Integrado | Mocks (parcial: el error solo se simuló) | EV-05, EV-06 |
| RNF-17 | Lógica en un solo lugar | Las pantallas comparten el mismo JavaScript y los cálculos oficiales viven en `database/sql/02_vistas.sql`. | Mantenibilidad | P0 | CONTRATO; README | Prototipos y plantillas cargan los mismos `comun.js`, `dashboard.js`, `registro.js` y `planificacion.js`. | Integrado | Mocks (consola de Planificación sin errores) | EV-07 |
| RNF-18 | Control de versiones e integración continua | Los cambios entran a `main` solo por pull request y las pruebas corren en GitHub. | Mantenibilidad | P0 | PLAN §7 (control 12); README | Todo cambio entra por PR con una aprobación y las pruebas en verde. | Integrado según el README | Reportado: el INFORME indica 150 pruebas automáticas satisfactorias con PostgreSQL. Sin registro de CI revisado por el Rol 4: un PR fusionado no demuestra que la CI esté en verde. Ver decisiones 8 y 9. | EV-09, EV-10 (prueban que los PR existen), EV-13 |
| RNF-19 | Despliegue con Docker Compose | El sistema se levanta con un solo comando. | Despliegue | P0 | PLAN §9; README | `docker compose up -d` levanta `db`, `web` y `n8n`. `GET /api/health` responde `{"estado":"ok","bd":"ok"}`. | Integrado | Pendiente | — |

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

### 9.2 Pendientes reales

Estos asuntos siguen abiertos al 8 de noviembre de 2026. No son preguntas para Quintana, sino trabajo o evidencia que falta.

| # | Pendiente | Responsable | Qué falta |
| --- | --- | --- | --- |
| 1 | Tablero de Power BI con sus cinco páginas (RF-29). | Olmer | Construir las páginas a partir de los CSV (EV-15) con la marca «Datos simulados» y la hoja de verificación. |
| 2 | Respaldo y restauración probada (RNF-13). | Sebastián (scripts) y Brayan (ejecución) | Entregar los scripts, ejecutar la restauración en `demanda360_restore` y guardar la evidencia. Hasta entonces, el RTO y el RPO siguen siendo objetivos. |
| 3 | Verificación de los riesgos inherentes. | Brayan | Revisar los valores de [trazabilidad_riesgos.md](trazabilidad_riesgos.md), que hoy son hipótesis del TALLER. |
| 4 | Evidencias de seguridad (401, 403, CSRF, puertos, token de n8n, `.env`). | Quintana y Brayan | Archivar capturas o registros de cada control. |
| 5 | Registro de las 150 pruebas automáticas y de la CI. | Quintana | Adjuntar el log de ejecución o el resultado de la CI para pasar EV-13 de «reportada» a «verificada». |
| 6 | Evidencia de la prueba real de n8n. | Quintana y Brayan | Archivar la ejecución en n8n, el correo recibido y la fila de la alerta (EV-14). |
| 7 | Criterios de demostración: 2 parciales y 2 pendientes de 13 (sección 3.5). | Equipo | Completarlos según el detalle del INFORME. |
| 8 | Ausencia de métrica general de rendimiento. | Equipo | Declarar la limitación; no crear un RNF nuevo sin un criterio aprobado por el equipo. |
| 9 | Selector de faltantes pendientes (RF-11). | Rol 4 | Probar el selector nuevo; hoy solo se probó escribir a mano el número de la atención. |

## 10. Respuestas y decisiones de Quintana

Las diez preguntas planteadas en la versión 1.1 fueron respondidas por Sebastián Quintana en la sección 5 del informe `estado_demanda360_8nov.md` (corte del 8 de noviembre de 2026). Las respuestas se registran como decisiones del equipo; las verificaciones y evidencias aún faltantes se mantienen identificadas en las secciones 3 y 9.2.

### 10.1 Decisiones del MVP

1. **Borradores (RF-20).** La API permite que ambos roles creen borradores: un trabajador puede proponer un pedido. La pantalla Planificación es exclusiva del propietario porque utiliza los sugeridos, que solo él consulta. Aprobar, enviar, confirmar y cancelar corresponde únicamente al propietario. Se conserva esta diferencia como decisión del MVP; no se cambia el código.
2. **Rotación y auditoría (RF-16 y RF-18).** Permanecen como funcionalidades de la API y como evidencia, sin una pantalla dedicada. La baja rotación aparece como estado del producto en el Dashboard. El propietario consulta la auditoría mediante `GET /api/auditoria` (criterio 13 de la demo).
3. **KPI 4 y 5 (RF-26 y RF-27).** No se muestran en el Dashboard de Flask, que presenta los KPI 1 a 3. Los KPI 4 y 5 están en la vista SQL, en `kpi_resumen.csv` y se visualizarán en Power BI. Para los datos de demostración: KPI 4 = **4,7 horas** (promedio de tres pedidos con respuesta; dos enviados sin respuesta se excluyen del promedio) y KPI 5 = **66,7 %** (dos de tres pedidos).
4. **Edición del umbral y contacto del proveedor.** Su modificación queda fuera del MVP. La limitación se registra en los riesgos R4 y R6; no se inventan rutas ni pantallas para administrarlos.
5. **Respaldo y restauración (RNF-13).** Al corte del informe, los scripts todavía no existen. **Sebastián (Rol 1)** debe crear `scripts/backup.sh` y `scripts/restore_prueba.sh`; **Brayan (Rol 2)** debe ejecutarlos y documentar la restauración en una base aislada. Las pruebas no se marcan como realizadas antes de disponer de sus resultados.

### 10.2 Aclaraciones documentales o de evidencia

6. **`GET /api/catalogos` en el contrato.** Quintana confirmó que ya aparece en la **fila 13** de la tabla de rutas de `docs/api/contrato.md`. Se cierra esta observación.
7. **Columna `origen_ref` en `conteos_fisicos`.** Quintana confirmó que existe como `varchar(64)` y tiene restricción `UNIQUE` denominada `uq_conteos_origen_ref`.
8. **CI y cobertura de pruebas.** Según Quintana, la CI ejecuta `pytest` con **PostgreSQL 16** en cada PR; se reportan 150 pruebas satisfactorias. Las familias documentadas son `test_auth` (inicio de sesión y 401), `test_roles` (403), `test_api_inventario` (productos, conteos, ventas, movimientos, 400 y 409), `test_esquema` (reglas de base de datos), `test_seguridad` (CSRF y errores sin trazas), `test_alertas` (alerta y reintentos), `test_api_analitica` y `test_kpi_demo` (KPI), `test_api_pedidos` (P1) y `test_pantallas` (interfaces). **Falta archivar o revisar los resultados concretos de CI** para pasar de prueba reportada a verificada; esta distribución por archivos no equivale a una matriz completa prueba–requerimiento.
9. **Protección de `main`.** Quintana confirmó que está activa: los cambios entran mediante PR y requieren aprobación de un revisor de `CODEOWNERS`. Esto no reemplaza la evidencia de una ejecución de CI.
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

> La justificación v4 se escribió antes del INFORME. Por eso todavía presenta RF-20 como pendiente y no menciona la prueba real de n8n (EV-14). La decisión vigente sobre RF-20 está en la sección 10 de este documento. No es necesario alterar el BPMN histórico por esa diferencia de corte.

## 12. Historial de cambios

| Versión | Fecha | Cambio | Autor |
| --- | --- | --- | --- |
| 1.0 | 8 nov 2026 | Primera versión: 29 RF, 19 RNF, diferencias, preguntas y cambios pendientes del TO-BE. | Jhonatan Rey (Rol 4) |
| 1.1 | 8 nov 2026 | Se distingue la ubicación de las evidencias (carpeta compartida o GitHub) y el estado de cada PR. Se precisa el rotulado de datos simulados en RNF-15. | Jhonatan Rey (Rol 4) |
| 1.2 | 8 nov 2026 | Se incorpora el informe de estado de Quintana: PR #1 a #10 en `main`, pantallas conectadas a la API real, 150 pruebas reportadas, prueba real de n8n, CSV de los KPI y valores de KPI 4 y 5. Se agrega el estado «Prueba reportada», la columna «Tipo» y las evidencias EV-12 a EV-16. Se actualizan los estados de RF-12 a RF-14, RF-20, RF-26 a RF-29, RNF-10, RNF-12, RNF-13 y RNF-18 sin cambiar criterios de aceptación. La sección 10 incorpora las diez respuestas textuales sintetizadas del informe de Quintana, y la sección 9 separa lo resuelto de los pendientes reales y la sección 11 cierra los ajustes del TO-BE con la v4 (PR #10). Las referencias al modelo vigente pasan del TO-BE v3 al v4. | Jhonatan Rey (Rol 4) |
