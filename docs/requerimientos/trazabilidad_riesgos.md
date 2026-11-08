# Trazabilidad de riesgos · Demanda360

| Campo | Valor |
| --- | --- |
| Proyecto | Demanda360 – MVP para Pinturas By-plus |
| Documento | Relación entre riesgos, controles, requerimientos y evidencias |
| Versión | 1.1 |
| Fecha | 8 de noviembre de 2026 |
| Elaborado por | Jhonatan Stiben Rey Velásquez (Rol 4) |
| Estado | En revisión con Quintana (Rol 1) y Brayan (Rol 2) |
| Documento relacionado | [Requerimientos RF y RNF](requerimientos.md) |

---

## 1. Propósito y advertencia

Este documento relaciona los seis riesgos de la matriz del Taller de Seguridad con los controles propuestos, los requerimientos del MVP que los atienden y las evidencias necesarias para comprobarlos.

Conviene leerlo con tres advertencias:

- **Los valores de probabilidad, impacto y riesgo residual son hipótesis académicas** del taller. No son mediciones ni resultados de Pinturas By-plus.
- El MVP aplica controles inspirados en ISO/IEC 27001 e ISO/IEC 27002:2022. Eso **no significa** que exista un sistema de gestión de seguridad de la información (SGSI) ni que la empresa esté certificada.
- **A la fecha no hay evidencias propias** de que los controles del backend, la restauración de respaldos o los procedimientos operativos funcionen. Los estados de implementación vienen de lo que declaran el contrato y el README.

Fuentes: Taller de Seguridad (4 nov 2026), Parte A y Parte B; plan del MVP, sección 7; `docs/api/contrato.md`; `README.md`. Los identificadores RF y RNF corresponden a [requerimientos.md](requerimientos.md).

## 2. Escala usada en el taller

| Probabilidad | Impacto | Nivel del riesgo (P × I) |
| --- | --- | --- |
| P1 baja: poco probable con el control operando | I1 bajo | 1–2: bajo |
| P2 media: posible | I2 medio | 3–4: medio |
| P3 alta: frecuente | I3 alto | 6–9: alto |

Los valores residuales son hipótesis sobre el estado después de implementar y probar los controles (taller, Parte A).

## 3. Matriz de trazabilidad

Valores de los estados:

- **Integrado:** el contrato o el README lo describen como implementado. No se ha verificado.
- **Sin confirmar:** no hay información de que exista.
- **Administrativo:** depende de una práctica de las personas, no del software.
- **Por confirmar:** la responsabilidad no está acordada.

| ID | Activo y dueño (taller) | Amenaza | Vulnerabilidad | Control propuesto (ISO/IEC 27002) | RF/RNF asociados | Responsable en el proyecto | Estado de implementación | Prueba requerida | Evidencia | Valoración residual propuesta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | Catálogo y saldos. Dueño: propietario de inventario. | Una carga de datos altera las existencias. | Referencias duplicadas o unidades incompatibles. | Validar SKU y unidad, rechazar duplicados y conciliar con el conteo (8.26). | RF-03, RF-05, RF-06, RF-08, RF-09, RNF-05, RNF-06, RNF-07 | Quintana (validaciones en el backend). La prueba de seguridad está por confirmar con Brayan. | Validaciones: integrado. Conciliación con el conteo: administrativo, sin procedimiento escrito. | SKU repetido → 409 `SKU_DUPLICADO`. Cantidad inválida → 400. Entrada o ajuste sin conteo → 409 `SIN_CONTEO`. | No hay evidencia propia del backend. Solo existe un 409 simulado en el prototipo (EV-06), que no sirve como prueba del control. | Alto (P2 × I3 = 6), hipótesis del taller |
| R2 | Historial de movimientos. Dueño: propietario de inventario. | Borrado o modificación sin autorización. | Cuenta compartida y edición directa de registros. | Cuentas individuales, permisos por rol y corrección por contramovimiento con bitácora (5.15 y 8.15). | RF-01, RF-02, RF-09, RF-17, RF-18, RNF-01, RNF-02, RNF-03, RNF-09 | Quintana (backend). La prueba de seguridad está por confirmar con Brayan. | Permisos, hash, bitácora y movimientos inmutables: integrado según el README. Cuentas individuales: pendiente de verificación (el README solo describe los usuarios demo). | Ruta sin sesión → 401. Trabajador → 403 en ajuste y aprobación. Ajuste sin justificación → 400. Consulta a `usuarios` con solo hashes. Consulta a `GET /api/auditoria`. | Pendiente. | Medio (P1 × I3 = 3), hipótesis del taller |
| R3 | Aplicación y acceso. Dueños: propietarios. | Falla del servicio o de internet. | Dependencia de una conexión y del acceso al servicio. | Formulario local foliado, copia disponible y ensayo de recuperación (5.29 y 5.30). | RNF-10, RNF-13, RNF-19, RNF-07 (evita duplicados si los folios se registran después con los formularios existentes) | Brayan (simulacro, por confirmar) y Quintana (plataforma). | Continuidad de la venta ante fallas de n8n: integrado. Plantilla de folios y simulacro: sin confirmar. | **Dos pruebas distintas** (ver sección 4.3): (a) venta con n8n apagado; (b) simulacro de caída y recuperación de Demanda360 en un entorno aislado. | Pendiente. | Medio (P2 × I2 = 4), hipótesis del taller |
| R4 | Pedidos y contactos de proveedores. Dueño: propietario de compras. | Suplantación de un proveedor por mensajería. | Cambios de número o de destino aceptados sin verificación. | Confirmar los cambios por el canal conocido y registrar la aprobación (5.15 y 6.3). | RF-17, RF-21, RF-22, RF-24, RNF-03, RNF-14 | Quintana (registro de la aprobación). Propietarios (verificación de contactos). | Aprobación de pedidos: integrado (P1). Verificación de contactos y capacitación: administrativo. | Trabajador intenta aprobar → 403. Transición inválida → 409 `TRANSICION_INVALIDA`. La auditoría registra `PEDIDO_APROBADO`. | Pendiente. La capacitación no está prevista en el plan del MVP. | Alto (P2 × I3 = 6), hipótesis del taller |
| R5 | Respaldos. Dueño: propietario designado. | Pérdida o cifrado de los datos y de sus copias. | Copias modificables desde la misma cuenta de operación. | Copias versionadas en una cuenta separada y restauración de prueba (8.13). | RNF-13, RNF-11 | Por confirmar con Quintana y Brayan, tanto quién escribe los scripts como quién los ejecuta. | Scripts de respaldo y restauración: sin confirmar. Copias en una cuenta separada: administrativo. | Respaldo con `pg_dump` fuera del repositorio. Restauración en una base de prueba aislada (`demanda360_restore`). Comparación de los conteos de las tablas y del saldo de tres referencias. Duración anotada. | Pendiente. El plan prevé un registro de respaldos; su ubicación final está por confirmar. | Medio (P1 × I3 = 3), hipótesis del taller |
| R6 | Reglas de reposición. Dueño: propietario de compras. | Cambio accidental del umbral o de la regla. | Edición sin prueba ni historial. | Versionar, probar con referencias de muestra y exigir aprobación (8.32). | RF-19, RNF-17, RNF-18 | Quintana (`02_vistas.sql` y CI). Propietarios (aprobación de cambios de regla). | Regla en SQL y cambios por PR: integrado según el README. Aprobación de cambios de regla por el propietario: administrativo. | **Dos tipos de prueba** (ver sección 4.6): (a) resultados de los KPI y del sugerido; (b) control de cambios, revisión y aprobación de la regla. | Pendiente. Los PR registrados (EV-09) muestran que hubo cambios, no que se revisó la regla. | Bajo (P1 × I2 = 2), hipótesis del taller |

## 4. Justificación por riesgo

### 4.1 R1. Catálogo y saldos

El sistema rechaza los SKU repetidos y las cantidades inválidas, y no permite entradas ni ajustes sobre productos que nunca se han contado. Estas validaciones reducen los errores de digitación, pero no detectan un saldo que parece razonable y está equivocado. Por eso el taller mantiene el residual en alto. El MVP no tiene una función de importación masiva: los datos entran por formularios y por la carga de datos demo. La conciliación con el conteo físico es una práctica de los propietarios y todavía no tiene un procedimiento escrito.

### 4.2 R2. Historial de movimientos

Los permisos por rol, la bitácora de solo inserción y los movimientos inmutables dificultan los cambios indebidos. Un usuario autorizado todavía puede registrar datos incorrectos, y por eso el residual queda en medio. El README describe la creación de un usuario demo por rol. No se sabe aún si el sistema permite crear cuentas individuales para cada persona, así que ese punto queda **pendiente de verificación**.

### 4.3 R3. Aplicación y acceso

Hay que separar dos pruebas que responden preguntas distintas:

| Prueba | Qué demuestra | Qué no demuestra |
| --- | --- | --- |
| (a) Venta con n8n apagado (plan §5) | Que una falla en el envío de la alerta no hace perder la venta (RNF-10) y que el reintento funciona (RF-14). | No demuestra la recuperación de Demanda360 ni el cumplimiento del RTO o del RPO. |
| (b) Simulacro de caída y recuperación (taller §9 y §11) | Cuánto se tarda en restaurar una copia, levantar la aplicación y verificar los saldos, y cuántos datos se perderían. | Solo vale para el entorno de prueba; no es una medición del negocio. |

El MVP **no tiene una función especial para importar folios manuales**. Cómo registrar los folios cuando el sistema vuelva a funcionar es un procedimiento que falta definir con las operaciones disponibles: atención, conteo, entrada y ajuste. El plan propone usar el número del folio como `origen_ref` para no registrarlo dos veces, pero eso todavía no está definido ni probado como procedimiento.

El simulacro debe hacerse en un **entorno aislado**, por ejemplo restaurando en la base de prueba `demanda360_restore`, **sin borrar ni afectar la base de trabajo del equipo**. La forma exacta se debe acordar con Brayan y Quintana.

**RTO de 4 horas y RPO de 1 hora:** son objetivos de diseño propuestos en el taller (§9). Solo se podrán comparar con los tiempos que mida el simulacro. Hoy no son resultados comprobados.

### 4.4 R4. Pedidos y contactos de proveedores

Este riesgo depende sobre todo de controles administrativos. El pedido se envía por WhatsApp o llamada fuera del sistema, y el MVP no tiene una ruta para editar el contacto del proveedor. Lo que aporta el sistema es que solo el propietario aprueba y que la aprobación queda registrada en la auditoría. Verificar los cambios de contacto por un canal conocido y capacitar al personal son prácticas de las personas. El residual sigue alto porque el canal conocido también puede estar comprometido.

### 4.5 R5. Respaldos

Un volumen de Docker conserva los datos al reiniciar el contenedor, pero no es un respaldo (plan §7). El control se cumple cuando existe una copia fuera del repositorio y se demuestra que se puede restaurar. Todavía no está confirmado si los scripts existen ni quién los escribe y ejecuta: según el README, el Rol 1 escribe y el Rol 2 ejecuta, pero esa asignación **debe acordarse con Quintana y Brayan** antes de presentarla como definitiva. Guardar copias versionadas en una cuenta separada es una práctica de operación propuesta en el taller.

### 4.6 R6. Reglas de reposición

Hay dos tipos de evidencia que no son equivalentes:

| Tipo | Ejemplo | Qué demuestra |
| --- | --- | --- |
| (a) Prueba de resultados | `backend/tests/test_kpi_demo.py` exige KPI 1 = 27,3 %, KPI 2 = 8,6 %, KPI 3 = 50 % y sugerido total = 54 con los datos demo. | Que la regla actual produce las cifras esperadas. Un cambio accidental que altere esas cifras haría fallar la prueba. |
| (b) Control de cambios | Historial de PR sobre `02_vistas.sql`, revisión de otra persona, campo `regla_version` y aprobación del propietario para cambiar la regla o el umbral. | Que cada cambio de la regla quedó registrado, se revisó y se aprobó. |

La prueba (a) está declarada, pero su resultado no se ha revisado. Para (b) no hay evidencia todavía: la existencia de PR no muestra que la regla se haya revisado ni aprobado. Además, el contrato no define una ruta para editar el umbral, así que hoy un cambio de umbral solo podría hacerse en la base o en los datos demo.

## 5. Controles administrativos y medidas fuera del MVP

Estas medidas del taller no se convierten en funcionalidades obligatorias del MVP:

| Medida del taller | Control | Tratamiento en el MVP |
| --- | --- | --- |
| Autenticación multifactor en cuentas de administración | 8.5 | No está en la aplicación. Solo está configurada en las cuentas de GitHub. |
| Alertas por ajustes masivos, repetidos o fuera de horario | 8.15 y 8.16 | Propuesta. El MVP solo alerta por stock crítico. |
| Restauración mensual y copias en una cuenta separada | 8.13 | Práctica de operación para un piloto. |
| Formulario local foliado durante una caída | 5.29 y 5.30 | Procedimiento operativo pendiente de definir. No hay una función de importación; los folios se registrarían después con los formularios existentes. |
| Verificación de contactos y capacitación contra mensajes falsos | 5.15, 6.3 y 6.8 | Práctica de las personas. |
| Protección física del equipo, las hojas de contingencia y el celular | 7.7, 7.8 y 7.9 | Práctica de las personas. |

## 6. Evidencias disponibles y faltantes

**Disponibles** (detalle en la sección 3.4 de [requerimientos.md](requerimientos.md)):

- Capturas de los prototipos con mocks (EV-01 a EV-06), guardadas en la carpeta compartida del proyecto. No se ha comprobado si están en GitHub.
- Revisión visual del 8 de noviembre (EV-07), sin captura.
- PR en GitHub: #4 (AS-IS), #5 y #6 (integración), fusionados en `main`; #7 (TO-BE), con su estado por verificar. Demuestran que hubo cambios, no que los controles funcionen.

**Faltantes:**

- Resultados propios de las pruebas de los controles del backend: 401, 403, 400, 409, CSRF y auditoría.
- Resultado de la CI en los PR.
- Ejecución de la alerta con n8n y de su reintento.
- Respaldo restaurado en una base de prueba aislada, con la duración medida.
- Procedimientos operativos escritos: folios manuales, conciliación con el conteo y verificación de contactos.

## 7. Limitaciones

- La matriz original del taller solo presenta el riesgo residual. No incluye el riesgo inherente (antes de los controles), que el plan pide agregar según la retroalimentación del taller. Este documento no inventa esos valores; completarlos le corresponde a quien mantiene la matriz de riesgos.
- Las valoraciones residuales requieren pruebas y la aceptación de los propietarios, como indica el taller.
- Las responsabilidades marcadas «por confirmar» no son asignaciones definitivas.
