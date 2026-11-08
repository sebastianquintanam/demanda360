# Trazabilidad de riesgos · Demanda360

| **Campo**             | **Valor**                                                                                                                               |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Proyecto              | Demanda360 – MVP para Pinturas By-plus                                                                                                  |
| Documento             | Relación entre riesgos, controles, requerimientos y evidencias                                                                          |
| Versión               | 1.2                                                                                                                                     |
| Fecha                 | 8 de noviembre de 2026                                                                                                                  |
| Elaborado por         | Jhonatan Stiben Rey Velásquez                                                                                                           |
| Estado                | Actualizada con el informe de Quintana (Rol 1) del 8 nov 2026; controles administrativos, riesgos inherentes y evidencias de seguridad pendientes                                                                                       |
| Documento relacionado | [Requerimientos RF y RNF](requerimientos.md) |

---

## 1. Propósito y advertencia

Este documento relaciona los seis riesgos de la matriz del Taller de Seguridad con los controles propuestos, los requerimientos del MVP que los atienden y las evidencias necesarias para comprobarlos.

Conviene leerlo con tres advertencias:

- **Los valores de probabilidad, impacto y riesgo residual son hipótesis académicas** del taller. No son mediciones ni resultados de Pinturas By-plus.
- El MVP aplica controles inspirados en ISO/IEC 27001 e ISO/IEC 27002:2022. Eso **no significa** que exista un sistema de gestión de seguridad de la información (SGSI) ni que la empresa esté certificada.
- **Quintana reportó** 150 pruebas automáticas satisfactorias con PostgreSQL y una prueba real de alerta por correo mediante n8n (`FALLIDA` → reintento → `ENVIADA`). Esos resultados se registran como **reportados**, no como comprobados personalmente por el Rol 4. Faltan adjuntar los registros de CI, las capturas de n8n y las evidencias de respaldo y restauración.

Fuentes: Taller de Seguridad (4 nov 2026), partes A y B; plan del MVP, sección 7; `docs/api/contrato.md`; `README.md`; informe de Quintana `estado_demanda360_8nov.md` (corte 8 nov 2026); [requerimientos.md](requerimientos.md), versión 1.2. Según el informe, los PR #1 a #10 están fusionados en `main`. La existencia de código o de un PR no equivale por sí sola a una prueba funcional.

## 2. Escala usada en el taller

| **Probabilidad**                               | **Impacto** | **Nivel del riesgo (P × I)** |
| ---------------------------------------------- | ----------- | ---------------------------- |
| P1 baja: poco probable con el control operando | I1 bajo     | 1–2: bajo                    |
| P2 media: posible                              | I2 medio    | 3–4: medio                   |
| P3 alta: frecuente                             | I3 alto     | 6–9: alto                    |

Los valores residuales son hipótesis sobre el escenario posterior a los controles (taller, parte A); **no están validados por mediciones del negocio**. La matriz original no aporta los valores de riesgo inherente: Brayan debe completarlos con su justificación, sin deducirlos automáticamente de los residuales.

## 3. Matriz de trazabilidad

Valores de los estados:

- **Integrado:** el contrato, el README o el informe describen la funcionalidad y el código integrado en `main`. No implica por sí mismo una prueba de funcionamiento.
- **Prueba reportada:** Quintana describe una ejecución satisfactoria, pero el Rol 4 no ha inspeccionado su registro o captura.
- **Pendiente de evidencia:** falta registrar la ejecución o archivar el soporte correspondiente.
- **Administrativo:** depende de un procedimiento o decisión de las personas, no solo del software.
- **Sin confirmar:** el código, artefacto o procedimiento no está acreditado en las fuentes disponibles.

| **ID** | **Activo y dueño (taller)** | **Amenaza** | **Vulnerabilidad** | **Control propuesto (ISO/IEC 27002)** | **RF/RNF asociados** | **Responsable en el proyecto** | **Estado de implementación** | **Prueba requerida** | **Evidencia** | **Valoración residual propuesta** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | Catálogo y saldos. Dueño: propietario de inventario. | Una carga de datos altera las existencias. | Referencias duplicadas o unidades incompatibles. | Validar SKU y unidad, rechazar duplicados y conciliar con el conteo (8.26). | RF-03, RF-05, RF-06, RF-08, RF-09, RNF-05, RNF-06, RNF-07 | Sebastián (backend y validaciones); Brayan (evidencia de seguridad). | Validaciones integradas en `main`. Conciliación física: control administrativo sin procedimiento escrito. | SKU repetido → 409 `SKU_DUPLICADO`. Cantidad inválida → 400. Entrada o ajuste sin conteo → 409 `SIN_CONTEO`. | EV-13: 150 pruebas con PostgreSQL reportadas por Quintana; el informe señala 409 de SKU y 400 de cantidad (sin logs revisados por Rol 4). EV-06 es solo un 409 simulado. Falta adjuntar pruebas específicas. | Alto (P2 × I3 = 6), hipótesis del taller |
| R2 | Historial de movimientos. Dueño: propietario de inventario. | Borrado o modificación sin autorización. | Cuenta compartida y edición directa de registros. | Cuentas individuales, permisos por rol y corrección por contramovimiento con bitácora (5.15 y 8.15). | RF-01, RF-02, RF-09, RF-17, RF-18, RNF-01, RNF-02, RNF-03, RNF-09 | Sebastián (backend y auditoría); Brayan (pruebas y evidencias de seguridad). | Permisos, hashes, bitácora y registros de solo inserción integrados según README e informe. Cuentas individuales fuera de los usuarios demo: sin verificar. | Ruta sin sesión → 401. Trabajador → 403 en ajuste y aprobación. Ajuste sin justificación → 400. Consulta a `usuarios` con solo hashes. Consulta a `GET /api/auditoria`. | EV-13: 150 pruebas reportadas; Quintana reporta un rechazo 403 al trabajador y consulta de auditoría en la demo. Falta evidencia archivada de 401, 403, hash, CSRF y auditoría. | Medio (P1 × I3 = 3), hipótesis del taller |
| R3 | Aplicación y acceso. Dueños: propietarios. | Falla del servicio o de internet. | Dependencia de una conexión y del acceso al servicio. | Formulario local foliado, copia disponible y ensayo de recuperación (5.29 y 5.30). | RNF-10, RNF-13, RNF-19, RNF-07 (evita duplicados si los folios se registran después con los formularios existentes) | Sebastián (scripts de respaldo/restauración y plataforma); Brayan (ejecución de recuperación y evidencias). | Continuidad de la venta ante caída de n8n: integrada y con prueba real reportada. Formularios foliados y recuperación total: pendientes. | **Dos pruebas distintas** (ver sección 4.3): (a) venta con n8n apagado; (b) simulacro de caída y recuperación de Demanda360 en un entorno aislado. | EV-14: Quintana reporta venta conservada con n8n apagado, alerta FALLIDA y reintento ENVIADA. No demuestra recuperación total ni RTO/RPO. Falta simulacro documentado y capturas. | Medio (P2 × I2 = 4), hipótesis del taller |
| R4 | Pedidos y contactos de proveedores. Dueño: propietario de compras. | Suplantación de un proveedor por mensajería. | Cambios de número o de destino aceptados sin verificación. | Confirmar los cambios por el canal conocido y registrar la aprobación (5.15 y 6.3). | RF-17, RF-21, RF-22, RF-24, RNF-03, RNF-14 | Sebastián (permisos, pedidos y auditoría); propietario de compras (verificación de contactos); Brayan (evidencia de seguridad). | Aprobación exclusiva del propietario integrada; verificación de contactos y capacitación siguen siendo controles administrativos sin evidencia de aplicación. | Trabajador intenta aprobar → 403. Transición inválida → 409 `TRANSICION_INVALIDA`. La auditoría registra `PEDIDO_APROBADO`. | EV-13: pruebas automáticas reportadas; el informe señala 403 al trabajador. No se ha inspeccionado un registro específico de aprobación, transición inválida y verificación de contacto. | Alto (P2 × I3 = 6), hipótesis del taller |
| R5 | Respaldos. Dueño: propietario designado. | Pérdida o cifrado de los datos y de sus copias. | Copias modificables desde la misma cuenta de operación. | Copias versionadas en una cuenta separada y restauración de prueba (8.13). | RNF-13, RNF-11 | Sebastián escribe `scripts/backup.sh` y `scripts/restore_prueba.sh`; Brayan ejecuta, registra y documenta las pruebas. | Al corte del informe faltan scripts y pruebas de respaldo/restauración. Copias versionadas en una cuenta separada: medida administrativa futura. | Respaldo con `pg_dump` fuera del repositorio. Restauración en una base de prueba aislada (`demanda360_restore`). Comparación de los conteos de las tablas y del saldo de tres referencias. Duración anotada. | Sin evidencia. Pendientes scripts, copia fuera del repositorio, restauración aislada y `docs/seguridad/registro_respaldos.md`; sin afirmar RTO/RPO cumplidos. | Medio (P1 × I3 = 3), hipótesis del taller |
| R6 | Reglas de reposición. Dueño: propietario de compras. | Cambio accidental del umbral o de la regla. | Edición sin prueba ni historial. | Versionar, probar con referencias de muestra y exigir aprobación (8.32). | RF-19, RNF-17, RNF-18 | Sebastián (reglas SQL y CI); Olmer (verificación de KPI); propietarios (decisión administrativa sobre cambios de regla). | Reglas SQL, PR y pruebas automáticas integrados/reportados; el control administrativo de aprobación de reglas no está documentado. | **Dos tipos de prueba** (ver sección 4.6): (a) resultados de los KPI y del sugerido; (b) control de cambios, revisión y aprobación de la regla. | EV-13: 150 pruebas reportadas; EV-15 y EV-16: CSV de KPI y resultados demo (KPI 4: 4,7 h; KPI 5: 66,7 %). Faltan logs, revisión de `test_kpi_demo.py` y evidencia de aprobación de cambios de regla. | Bajo (P1 × I2 = 2), hipótesis del taller |

## 4. Justificación por riesgo

### 4.1 R1. Catálogo y saldos

El sistema rechaza los SKU repetidos y las cantidades inválidas, y no permite entradas ni ajustes sobre productos que nunca se han contado. Estas validaciones reducen los errores de digitación, pero no detectan un saldo que parece razonable y está equivocado. Por eso el taller mantiene el residual en alto. El MVP no tiene una función de importación masiva: los datos entran por formularios y por la carga de datos demo. La conciliación con el conteo físico es una práctica de los propietarios y todavía no tiene un procedimiento escrito.

### 4.2 R2. Historial de movimientos

Los permisos por rol, la bitácora de solo inserción y los movimientos inmutables dificultan los cambios indebidos. Un usuario autorizado todavía puede registrar datos incorrectos, y por eso el residual queda en medio. El README describe la creación de un usuario demo por rol. No se sabe aún si el sistema permite crear cuentas individuales para cada persona, así que ese punto queda **pendiente de verificación**.

### 4.3 R3. Aplicación y acceso

Hay que separar dos pruebas que responden preguntas distintas:

| **Prueba**                                              | **Qué demuestra**                                                                                                    | **Qué no demuestra**                                                             |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| (a) Venta con n8n apagado (plan §5)                     | Que una falla en el envío de la alerta no hace perder la venta (RNF-10) y que el reintento funciona (RF-14).         | No demuestra la recuperación de Demanda360 ni el cumplimiento del RTO o del RPO. |
| (b) Simulacro de caída y recuperación (taller §9 y §11) | Cuánto se tarda en restaurar una copia, levantar la aplicación y verificar los saldos, y cuántos datos se perderían. | Solo vale para el entorno de prueba; no es una medición del negocio.             |

El MVP **no tiene una función especial para importar folios manuales**. Cómo registrar los folios cuando el sistema vuelva a funcionar es un procedimiento que falta definir con las operaciones disponibles: atención, conteo, entrada y ajuste. El plan propone usar el número del folio como `origen_ref` para no registrarlo dos veces, pero eso todavía no está definido ni probado como procedimiento.

El informe de Quintana reporta una prueba exitosa de continuidad de la venta durante una caída de n8n (EV-14). **Esta prueba no mide la recuperación del sistema**. El simulacro de respaldo y restauración todavía debe realizarse en una base aislada, por ejemplo `demanda360_restore`, **sin borrar ni afectar la base de trabajo**; Sebastián prepara los scripts y Brayan ejecuta y documenta la prueba.

**RTO de 4 horas y RPO de 1 hora:** son objetivos de diseño propuestos en el taller (§9). Solo se podrán comparar con los tiempos que mida el simulacro. Hoy no son resultados comprobados.

### 4.4 R4. Pedidos y contactos de proveedores

Este riesgo depende sobre todo de controles administrativos. El pedido se envía por WhatsApp o llamada fuera del sistema, y el MVP no tiene una ruta para editar el contacto del proveedor. Lo que aporta el sistema es que solo el propietario aprueba y que la aprobación queda registrada en la auditoría. Verificar los cambios de contacto por un canal conocido y capacitar al personal son prácticas de las personas. El residual sigue alto porque el canal conocido también puede estar comprometido.

### 4.5 R5. Respaldos

Un volumen de Docker conserva los datos al reiniciar el contenedor, pero no es un respaldo (plan §7). El control se cumple cuando existe una copia fuera del repositorio y se demuestra que se puede restaurar. Según el informe de Quintana del 8 de noviembre, los scripts aún no estaban listos y la responsabilidad está definida: **Sebastián los escribe y Brayan los ejecuta y documenta**. No hay evidencia todavía de una restauración correcta. Guardar copias versionadas en una cuenta separada es una práctica de operación propuesta en el taller.

### 4.6 R6. Reglas de reposición

Hay dos tipos de evidencia que no son equivalentes:

| **Tipo**                 | **Ejemplo**                                                                                                                                            | **Qué demuestra**                                                                                                     |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| (a) Prueba de resultados | `backend/tests/test_kpi_demo.py` exige KPI 1 = 27,3 %, KPI 2 = 8,6 %, KPI 3 = 50 % y sugerido total = 54 con los datos demo.                           | Que la regla actual produce las cifras esperadas. Un cambio accidental que altere esas cifras haría fallar la prueba. |
| (b) Control de cambios   | Historial de PR sobre `02_vistas.sql`, revisión de otra persona, campo `regla_version` y aprobación del propietario para cambiar la regla o el umbral. | Que cada cambio de la regla quedó registrado, se revisó y se aprobó.                                                  |

El informe reporta 150 pruebas con PostgreSQL y los CSV de los KPI (EV-13, EV-15 y EV-16), pero el Rol 4 aún no revisó la salida específica de `test_kpi_demo.py` ni la comparación del Excel de Olmer. Para (b) sigue sin haber evidencia de aprobación de cambios de regla por parte del propietario: que los PR estén fusionados no demuestra esa aprobación operativa. Además, el contrato no define una ruta para editar el umbral, así que hoy un cambio de umbral solo podría hacerse en la base o en los datos demo.

## 5. Controles administrativos y medidas fuera del MVP

Estas medidas del taller no se convierten en funcionalidades obligatorias del MVP:

| **Medida del taller**                                                | **Control**     | **Tratamiento en el MVP**                                                                                                                           |
| -------------------------------------------------------------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Autenticación multifactor en cuentas de administración               | 8.5             | No está en la aplicación. Solo está configurada en las cuentas de GitHub.                                                                           |
| Alertas por ajustes masivos, repetidos o fuera de horario            | 8.15 y 8.16     | Propuesta. El MVP solo alerta por stock crítico.                                                                                                    |
| Restauración mensual y copias en una cuenta separada                 | 8.13            | Práctica de operación para un piloto.                                                                                                               |
| Formulario local foliado durante una caída                           | 5.29 y 5.30     | Procedimiento operativo pendiente de definir. No hay una función de importación; los folios se registrarían después con los formularios existentes. |
| Verificación de contactos y capacitación contra mensajes falsos      | 5.15, 6.3 y 6.8 | Práctica de las personas.                                                                                                                           |
| Protección física del equipo, las hojas de contingencia y el celular | 7.7, 7.8 y 7.9  | Práctica de las personas.                                                                                                                           |

## 6. Evidencias disponibles, reportadas y pendientes

Para evitar duplicaciones, los códigos EV citados aquí corresponden a la sección 3.4 de [requerimientos.md](requerimientos.md), versión 1.2.

**Documentación y evidencias de prototipo disponibles:**

- EV-01 a EV-06: capturas con mocks; muestran pantallas, no pruebas de la API.
- EV-07: revisión visual del Rol 4 del 8 de noviembre, sin captura guardada.
- EV-09 y EV-10: PR de integración y BPMN, incluido el PR #10 del TO-BE v4, fusionados en `main` según el informe de Quintana. Demuestran incorporación del código y documentos, no resultados de ejecución.

**Pruebas y resultados reportados por Sebastián, todavía sin soporte revisado por el Rol 4:**

- EV-12: informe `estado_demanda360_8nov.md` (corte 8 nov 2026).
- EV-13: 150 pruebas automáticas satisfactorias contra PostgreSQL real, según el informe. Faltan logs o resultados de CI para vincular cada prueba con el control.
- EV-14: prueba de alerta real con n8n: venta registrada con n8n apagado, alerta `FALLIDA`, ejecución posterior del reintento, estado `ENVIADA` y correo recibido; se utilizó el mismo `evento_id`. Faltan capturas censuradas de base, n8n y correo.
- EV-15 y EV-16: existencia reportada de cinco CSV y resultados con datos demo, KPI 4 = 4,7 horas y KPI 5 = 66,7 %. Queda pendiente revisión de Olmer y Power BI.

**Pendientes para comprobar los controles:**

- Evidencias de 401, 403, 400, 409, CSRF, auditoría, restricciones de red y protección de secretos (Sebastián y Brayan).
- Prueba de que una segunda venta bajo el umbral no vuelve a enviar la alerta, y casos de token inválido, si no se incluyen ya en la evidencia automatizada (Sebastián y Brayan).
- Registro de CI y relación de las pruebas con los RF/RNF (Sebastián).
- Scripts de copia y restauración, simulacro aislado en `demanda360_restore`, comparación de conteos y saldos, y duración registrada (Sebastián y Brayan).
- Procedimientos de folios manuales, conciliación física y verificación de contactos, de naturaleza administrativa.

**La prueba de n8n no demuestra respaldo, restauración, cumplimiento del RTO o del RPO ni reducción efectiva del riesgo residual.**

## 7. Limitaciones

- La matriz original del taller solo presenta riesgo residual. **No incluye riesgo inherente** (antes de los controles): Brayan debe completar y justificar esos valores; aquí no se inventan ni se deducen de los residuales.
- Las valoraciones residuales siguen siendo hipótesis académicas y requieren validación de controles y aceptación de los propietarios; no se han recalculado con resultados de una operación real.
- La prueba reportada de n8n y las 150 pruebas automáticas no reemplazan la evidencia específica de cada control ni los procedimientos administrativos.
- Los objetivos RTO = 4 horas y RPO = 1 hora continúan sujetos a un simulacro de restauración, no son resultados logrados.

## 8. Historial de cambios

| Versión | Fecha | Cambio | Responsable |
| --- | --- | --- | --- |
| 1.1 | 8 nov 2026 | Matriz de trazabilidad de seis riesgos, controles, requerimientos y valores residuales según el Taller de Seguridad. | Jhonatan (Rol 4) |
| 1.2 | 8 nov 2026 | Incorporación del informe de Quintana: PR #1 a #10, pruebas automáticas y de n8n reportadas, KPI demo, asignación de respaldos y pendientes documentales. Se conservan íntegros los valores residuales y se deja pendiente el riesgo inherente a cargo de Brayan. | Jhonatan (Rol 4) |
