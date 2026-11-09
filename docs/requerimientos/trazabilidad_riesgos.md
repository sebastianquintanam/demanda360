# Trazabilidad de riesgos · Demanda360

| **Campo**             | **Valor**                                                                                                                               |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Proyecto              | Demanda360 – MVP para Pinturas By-plus                                                                                                  |
| Documento             | Relación entre riesgos, controles, requerimientos y evidencias                                                                          |
| Versión               | 1.3                                                                                                                                     |
| Fecha                 | 8 de noviembre de 2026                                                                                                                  |
| Elaborado por         | Jhonatan Stiben Rey Velásquez                                                                                                           |
| Estado                | Conciliada con auditoría del 8 nov 2026 (21:15): CI, alertas, respaldos, seguridad y KPI con evidencia; riesgos inherentes y controles administrativos aún pendientes                                                                                       |
| Documento relacionado | [Requerimientos RF y RNF](requerimientos.md) |

---

## 1. Propósito y advertencia

Este documento relaciona los seis riesgos de la matriz del Taller de Seguridad con los controles propuestos, los requerimientos del MVP que los atienden y las evidencias necesarias para comprobarlos.

Conviene leerlo con tres advertencias:

- **Los valores de probabilidad, impacto y riesgo residual son hipótesis académicas** del taller. No son mediciones ni resultados de Pinturas By-plus.
- El MVP aplica controles inspirados en ISO/IEC 27001 e ISO/IEC 27002:2022. Eso **no significa** que exista un sistema de gestión de seguridad de la información (SGSI) ni que la empresa esté certificada.
- **La auditoría final de Quintana** documenta 150 pruebas en verde sobre `main` con captura de CI, el error real 409 por SKU duplicado, la recuperación de alertas n8n (`FALLIDA` → reintento → `ENVIADA`) y evidencias de respaldo y restauración. No son pruebas ejecutadas por el Rol 4; las capturas de la demo y algunos controles individuales siguen pendientes.

Fuentes: Taller de Seguridad (4 nov 2026), partes A y B; plan del MVP, sección 7; `docs/api/contrato.md`; `README.md`; informes de Quintana `estado_demanda360_8nov.md` y `auditoria_demanda360_8nov.md` (corte 8 nov 21:15); [requerimientos.md](requerimientos.md), versión 1.3. Según la auditoría, los PR #1–#20 están fusionados en `main`. La existencia de código o de un PR no equivale por sí sola a una prueba funcional.

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
- **Evidencia archivada:** existe una captura o registro localizable; se limita a lo que efectivamente muestra. Para pruebas sin captura individual se utiliza **CI global documentada** o **reportado sin soporte individual**.
- **Pendiente de evidencia:** falta registrar una ejecución o archivar el soporte concreto. No equivale a que el código no exista.
- **Administrativo:** depende de un procedimiento o decisión de las personas, no solo del software.
- **Sin confirmar:** el código, artefacto o procedimiento no está acreditado en las fuentes disponibles.

| **ID** | **Activo y dueño (taller)** | **Amenaza** | **Vulnerabilidad** | **Control propuesto (ISO/IEC 27002)** | **RF/RNF asociados** | **Responsable en el proyecto** | **Estado de implementación** | **Prueba requerida** | **Evidencia** | **Valoración residual propuesta** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | Catálogo y saldos. Dueño: propietario de inventario. | Una carga de datos altera las existencias. | Referencias duplicadas o unidades incompatibles. | Validar SKU y unidad, rechazar duplicados y conciliar con el conteo (8.26). | RF-03, RF-05, RF-06, RF-08, RF-09, RNF-05, RNF-06, RNF-07 | Sebastián (backend y validaciones); Brayan (evidencia de seguridad). | Validaciones de catálogo integradas. 409 por SKU duplicado con captura; conciliación física es control administrativo todavía sin procedimiento aprobado. | SKU repetido → 409 `SKU_DUPLICADO`. Cantidad inválida → 400. Entrada o ajuste sin conteo → 409 `SIN_CONTEO`. | EV-18 (`docs/evidencias/EV_BACKEND_02_error_409_sku_duplicado.png`) muestra 409 real por SKU; EV-13 documenta CI global. Cantidad inválida y `SIN_CONTEO` requieren demostración individual en el video. No confundir SKU duplicado con `SIN_CONTEO`. | Alto (P2 × I3 = 6), hipótesis del taller |
| R2 | Historial de movimientos. Dueño: propietario de inventario. | Borrado o modificación sin autorización. | Cuenta compartida y edición directa de registros. | Cuentas individuales, permisos por rol y corrección por contramovimiento con bitácora (5.15 y 8.15). | RF-01, RF-02, RF-09, RF-17, RF-18, RNF-01, RNF-02, RNF-03, RNF-09 | Sebastián (backend y auditoría); Brayan (pruebas y evidencias de seguridad). | Roles, hashes, movimientos inmutables y auditoría integrados según código e informe; solo dos cuentas demo compartidas por rol, **no cuentas individuales por persona**. | Ruta sin sesión → 401. Trabajador → 403 en ajuste y aprobación. Ajuste sin justificación → 400. Consulta a `usuarios` con solo hashes. Consulta a `GET /api/auditoria`. | EV-13 documenta pruebas globales; AUDITORÍA programa 403 del trabajador, trigger y consulta de auditoría para grabación. La seguridad de cuentas personales no se afirma implementada. | Medio (P1 × I3 = 3), hipótesis del taller |
| R3 | Aplicación y acceso. Dueños: propietarios. | Falla del servicio o de internet. | Dependencia de una conexión y del acceso al servicio. | Formulario local foliado, copia disponible y ensayo de recuperación (5.29 y 5.30). | RNF-10, RNF-13, RNF-19, RNF-07 (evita duplicados si los folios se registran después con los formularios existentes) | Sebastián (scripts de respaldo/restauración y plataforma); Brayan (ejecución de recuperación y evidencias). | Venta conserva estado ante fallo de n8n; scripts y restauración aislada documentados. Formularios foliados y recuperación operativa completa continúan pendientes. | **Dos pruebas distintas** (ver sección 4.3): (a) venta con n8n apagado; (b) simulacro de caída y recuperación de Demanda360 en un entorno aislado. | EV-14: alerta FALLIDA → ENVIADA y correo. EV-19: `02_respaldo_postgresql.png`, `03_restauracion_verificada.png` y registro de respaldo. No hay prueba de RTO/RPO del negocio ni del procedimiento de folios. | Medio (P2 × I2 = 4), hipótesis del taller |
| R4 | Pedidos y contactos de proveedores. Dueño: propietario de compras. | Suplantación de un proveedor por mensajería. | Cambios de número o de destino aceptados sin verificación. | Confirmar los cambios por el canal conocido y registrar la aprobación (5.15 y 6.3). | RF-17, RF-21, RF-22, RF-24, RNF-03, RNF-14 | Sebastián (permisos, pedidos y auditoría); propietario de compras (verificación de contactos); Brayan (evidencia de seguridad). | Permiso de aprobación solo del propietario y auditoría integrados; verificación de identidad/contactos de proveedores sigue siendo administrativa y no demostrada. | Trabajador intenta aprobar → 403. Transición inválida → 409 `TRANSICION_INVALIDA`. La auditoría registra `PEDIDO_APROBADO`. | EV-13: CI global; demostración pendiente de 403 del trabajador y auditoría. No existe soporte operativo de verificación de cambio de contacto. | Alto (P2 × I3 = 6), hipótesis del taller |
| R5 | Respaldos. Dueño: propietario designado. | Pérdida o cifrado de los datos y de sus copias. | Copias modificables desde la misma cuenta de operación. | Copias versionadas en una cuenta separada y restauración de prueba (8.13). | RNF-13, RNF-11 | Sebastián escribe `scripts/backup.sh` y `scripts/restore_prueba.sh`; Brayan ejecuta, registra y documenta las pruebas. | Scripts `scripts/backup.sh` y `scripts/restore_prueba.sh` presentes; copia y restauración aislada documentadas según auditoría. Copias versionadas en cuenta separada siguen como medida operativa propuesta. | Respaldo con `pg_dump` fuera del repositorio. Restauración en una base de prueba aislada (`demanda360_restore`). Comparación de los conteos de las tablas y del saldo de tres referencias. Duración anotada. | EV-19: `docs/evidencias/02_respaldo_postgresql.png`, `03_restauracion_verificada.png`, `docs/seguridad/registro_respaldos.md`. Ensayo técnico ≠ continuidad operativa comprobada; RTO/RPO siguen sin acreditarse. | Medio (P1 × I3 = 3), hipótesis del taller |
| R6 | Reglas de reposición. Dueño: propietario de compras. | Cambio accidental del umbral o de la regla. | Edición sin prueba ni historial. | Versionar, probar con referencias de muestra y exigir aprobación (8.32). | RF-19, RNF-17, RNF-18 | Sebastián (reglas SQL y CI); Olmer (verificación de KPI); propietarios (decisión administrativa sobre cambios de regla). | SQL, pruebas y tablero Power BI documentados; la aprobación operativa de cambios de reglas por el propietario aún no está formalizada. | **Dos tipos de prueba** (ver sección 4.6): (a) resultados de los KPI y del sugerido; (b) control de cambios, revisión y aprobación de la regla. | EV-13 (CI), EV-15 (CSV) y EV-16 (cinco KPI cotejados con Power BI) según AUDITORÍA. PR revisados no demuestran aprobación de un cambio comercial de reglas. | Bajo (P1 × I2 = 2), hipótesis del taller |

## 4. Justificación por riesgo

### 4.1 R1. Catálogo y saldos

El sistema rechaza los SKU repetidos y las cantidades inválidas, y no permite entradas ni ajustes sobre productos que nunca se han contado. Estas validaciones reducen los errores de digitación, pero no detectan un saldo que parece razonable y está equivocado. Por eso el taller mantiene el residual en alto. El MVP no tiene una función de importación masiva: los datos entran por formularios y por la carga de datos demo. La conciliación con el conteo físico es una práctica de los propietarios y todavía no tiene un procedimiento escrito.

### 4.2 R2. Historial de movimientos

Los permisos por rol, la bitácora de solo inserción y los movimientos inmutables dificultan los cambios indebidos. Un usuario autorizado todavía puede registrar datos incorrectos, y por eso el residual queda en medio. El README describe la creación de un usuario demo por rol. La auditoría confirma que el MVP **solo incluye dos cuentas de demostración**, una por rol; no implementa cuentas individuales por persona. Ese riesgo debe conservarse como limitación explícita.

### 4.3 R3. Aplicación y acceso

Hay que separar dos pruebas que responden preguntas distintas:

| **Prueba**                                              | **Qué demuestra**                                                                                                    | **Qué no demuestra**                                                             |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| (a) Venta con n8n apagado (plan §5)                     | Que una falla en el envío de la alerta no hace perder la venta (RNF-10) y que el reintento funciona (RF-14).         | No demuestra la recuperación de Demanda360 ni el cumplimiento del RTO o del RPO. |
| (b) Simulacro de caída y recuperación (taller §9 y §11) | Cuánto se tarda en restaurar una copia, levantar la aplicación y verificar los saldos, y cuántos datos se perderían. | Solo vale para el entorno de prueba; no es una medición del negocio.             |

El MVP **no tiene una función especial para importar folios manuales**. Cómo registrar los folios cuando el sistema vuelva a funcionar es un procedimiento que falta definir con las operaciones disponibles: atención, conteo, entrada y ajuste. El plan propone usar el número del folio como `origen_ref` para no registrarlo dos veces, pero eso todavía no está definido ni probado como procedimiento.

La auditoría de Quintana ya vincula capturas de la venta ante caída de n8n (EV-14) y del **respaldo con restauración aislada** (EV-19). **Estas son pruebas distintas:** una acredita la continuidad de la venta frente al fallo de alertas; la otra demuestra que se pudo recuperar una copia en un entorno de ensayo. Ninguna por sí sola mide cuánto tardaría una recuperación completa de la operación del comercio ni cuánta información se perdería en ese escenario.

**RTO de 4 horas y RPO de 1 hora:** son objetivos de diseño propuestos en el taller (§9). Solo se podrán comparar con los tiempos que mida el simulacro. Hoy no son resultados comprobados.

### 4.4 R4. Pedidos y contactos de proveedores

Este riesgo depende sobre todo de controles administrativos. El pedido se envía por WhatsApp o llamada fuera del sistema, y el MVP no tiene una ruta para editar el contacto del proveedor. Lo que aporta el sistema es que solo el propietario aprueba y que la aprobación queda registrada en la auditoría. Verificar los cambios de contacto por un canal conocido y capacitar al personal son prácticas de las personas. El residual sigue alto porque el canal conocido también puede estar comprometido.

### 4.5 R5. Respaldos

Un volumen de Docker conserva los datos al reiniciar el contenedor, pero no es un respaldo (plan §7). El control se cumple cuando existe una copia fuera del repositorio y se demuestra que se puede restaurar. En el informe inicial faltaban scripts; la auditoría posterior registra que **Sebastián incorporó los scripts y Brayan aportó la evidencia** de respaldo y restauración aislada (`docs/seguridad/registro_respaldos.md` y capturas en `docs/evidencias/`). No hay prueba de cumplimiento operativo del RTO de 4 horas ni del RPO de 1 hora en la empresa. Guardar copias versionadas en una cuenta separada es una práctica de operación propuesta en el taller.

### 4.6 R6. Reglas de reposición

Hay dos tipos de evidencia que no son equivalentes:

| **Tipo**                 | **Ejemplo**                                                                                                                                            | **Qué demuestra**                                                                                                     |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| (a) Prueba de resultados | `backend/tests/test_kpi_demo.py` exige KPI 1 = 27,3 %, KPI 2 = 8,6 %, KPI 3 = 50 % y sugerido total = 54 con los datos demo.                           | Que la regla actual produce las cifras esperadas. Un cambio accidental que altere esas cifras haría fallar la prueba. |
| (b) Control de cambios   | Historial de PR sobre `02_vistas.sql`, revisión de otra persona, campo `regla_version` y aprobación del propietario para cambiar la regla o el umbral. | Que cada cambio de la regla quedó registrado, se revisó y se aprobó.                                                  |

La auditoría y las evidencias EV-13, EV-15 y EV-16 documentan 150 pruebas en verde y coincidencia de los cinco KPI en SQL, CSV, Excel, fichas y Power BI. Eso respalda el cálculo de prueba, pero no reemplaza la aprobación operativa de las reglas. Para (b) sigue sin haber evidencia de aprobación de cambios de regla por parte del propietario: que los PR estén fusionados no demuestra esa aprobación operativa. Además, el contrato no define una ruta para editar el umbral, así que hoy un cambio de umbral solo podría hacerse en la base o en los datos demo.

## 5. Controles administrativos y medidas fuera del MVP

Estas medidas del taller no se convierten en funcionalidades obligatorias del MVP:

| **Medida del taller**                                                | **Control**     | **Tratamiento en el MVP**                                                                                                                           |
| -------------------------------------------------------------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Autenticación multifactor en cuentas de administración               | 8.5             | No está en la aplicación. Solo está configurada en las cuentas de GitHub.                                                                           |
| Alertas por ajustes masivos, repetidos o fuera de horario            | 8.15 y 8.16     | Propuesta. El MVP solo alerta por stock crítico.                                                                                                    |
| Restauración mensual y copias en una cuenta separada                 | 8.13            | La restauración aislada de prueba quedó documentada; periodicidad, separación de cuentas y operación continua siguen siendo propuestas para un piloto.                                                                                                               |
| Formulario local foliado durante una caída                           | 5.29 y 5.30     | Procedimiento operativo pendiente de definir. No hay una función de importación; los folios se registrarían después con los formularios existentes. |
| Verificación de contactos y capacitación contra mensajes falsos      | 5.15, 6.3 y 6.8 | Práctica de las personas.                                                                                                                           |
| Protección física del equipo, las hojas de contingencia y el celular | 7.7, 7.8 y 7.9  | Práctica de las personas.                                                                                                                           |

## 6. Evidencias disponibles, reportadas y pendientes

Los códigos EV corresponden a la sección 3.4 de [requerimientos.md](requerimientos.md), versión 1.3.

**Evidencias incorporadas y localizables en el repositorio (según la auditoría y la revisión de las capturas recibidas):**

- **EV-17:** seis capturas de las cinco comprobaciones visuales del Rol 4 (`docs/evidencias/EV_R4_*.png`). **Son mocks**, no pruebas de Flask.
- **EV-18:** respuesta real `409 CONFLICT` por SKU duplicado (`docs/evidencias/EV_BACKEND_02_error_409_sku_duplicado.png`). No cubre `409 SIN_CONTEO`.
- **EV-13:** 150 pruebas automatizadas aprobadas sobre `main`, con captura (`docs/evidencias/EV_BACKEND_01_150_pruebas_ci.png`). Sin matriz individual de cobertura RF/RNF.
- **EV-14:** cuatro capturas y un LEEME del escenario de n8n: fallo, reintento, éxito y correo.
- **EV-19:** evidencia del respaldo y restauración aislada, con registro en `docs/seguridad/registro_respaldos.md`. Es una prueba técnica, **no un simulacro completo de RTO/RPO operativo**.
- **EV-15/EV-16:** cinco KPI de datos simulados coincidentes entre SQL, CSV, Excel, fichas y Power BI según auditoría; tablero en `analytics/powerbi/demanda360.pbix`.
- **EV-20/EV-21:** despliegue con puertos locales y revisión de secretos del historial Git documentados por Quintana.

**Evidencias o medidas todavía pendientes:**

- Fotogramas en aplicación Flask real para los criterios de demostración **1, 3, 4–7 y 13**. La suite en verde no sustituye cada captura.
- Capturas adicionales prometidas por Sebastián: segunda venta bajo umbral sin alerta duplicada y alerta `FALLIDA` visible en Registro.
- **Riesgo inherente de los seis riesgos**, con justificación, a cargo de **Brayan**. La matriz del taller solo conserva valoración residual; no inventar P/I inherentes.
- **Controles administrativos:** cuentas individuales (el MVP usa dos cuentas demo), conciliación física periódica, recuperación de folios manuales, verificación de identidad de proveedor y aceptación/seguimiento de riesgos residuales altos.
- RTO = 4 h y RPO = 1 h son objetivos académicos por validar mediante ejercicio representativo, no desempeños medidos del negocio.

**Delimitación:** la prueba exitosa de n8n no demuestra restauración; la prueba de restauración aislada no demuestra continuidad integral ni objetivo operativo de RTO/RPO. Las métricas demo no prueban mejoras reales en Pinturas By-plus.

## 7. Limitaciones

- La matriz original del taller solo presenta riesgo residual. **No incluye riesgo inherente** (antes de los controles): Brayan debe completar y justificar esos valores; aquí no se inventan ni se deducen de los residuales.
- Las valoraciones residuales siguen siendo hipótesis académicas y requieren validación de controles y aceptación de los propietarios; no se han recalculado con resultados de una operación real.
- Las capturas archivadas de n8n, las 150 pruebas automáticas y el 409 por SKU no reemplazan la evidencia específica de todos los escenarios ni los procedimientos administrativos.
- Los objetivos RTO = 4 horas y RPO = 1 hora continúan sujetos a un simulacro de restauración, no son resultados logrados.

## 8. Historial de cambios

| Versión | Fecha | Cambio | Responsable |
| --- | --- | --- | --- |
| 1.1 | 8 nov 2026 | Matriz de trazabilidad de seis riesgos, controles, requerimientos y valores residuales según el Taller de Seguridad. | Jhonatan (Rol 4) |
| 1.2 | 8 nov 2026 | Incorporación del informe de Quintana: PR #1 a #10, pruebas automáticas y de n8n reportadas, KPI demo, asignación de respaldos y pendientes documentales. Se conservan íntegros los valores residuales y se deja pendiente el riesgo inherente a cargo de Brayan. | Jhonatan (Rol 4) |
| 1.3 | 8 nov 2026 | Se concilian estados y soportes con auditoría de Quintana de las 21:15: CI, 409 real por SKU duplicado, alertas, restauración, Power BI y controles de seguridad. Se conservan **sin cambios** los seis valores residuales (R1=6, R2=3, R3=4, R4=6, R5=3, R6=2), y el riesgo inherente permanece pendiente de Brayan. No se afirma certificación ISO ni cumplimiento de RTO/RPO. | Jhonatan (Rol 4) |
