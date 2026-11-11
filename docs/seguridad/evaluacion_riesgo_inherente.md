# Evaluación del riesgo inherente — Demanda360

**Proyecto:** Demanda360 — Pinturas By-plus  
**Responsable:** Brayan Felipe Álvarez Nieto  
**Tipo de evaluación:** Cualitativa, con fines académicos  
**Estado:** Propuesta pendiente de validación por el equipo y los propietarios

## 1. Metodología

El riesgo inherente corresponde a la exposición previa a la aplicación de los controles de seguridad propuestos. Se evalúa mediante la probabilidad de ocurrencia y el impacto potencial.

Se utiliza la escala del Taller de Seguridad de Demanda360:

- P1: probabilidad baja.
- P2: probabilidad media.
- P3: probabilidad alta.
- I1: impacto bajo.
- I2: impacto medio.
- I3: impacto alto.

**Fórmula:** Riesgo inherente = Probabilidad × Impacto.

Clasificación: bajo (1–2), medio (3–4), alto (6–9).

Las valoraciones representan juicios técnicos sobre los escenarios identificados, no frecuencias históricas verificadas en Pinturas By-plus.

## 2. Evaluaciones individuales

### R1. Alteración del catálogo y los saldos

**Probabilidad inherente propuesta:** P3 — Alta.  
**Impacto inherente:** I3 — Alto.  
**Resultado:** 9 — Riesgo alto.

Sin validaciones de SKU, unidad y cantidad, el registro frecuente de movimientos puede introducir duplicados, inconsistencias o cantidades incorrectas. La exposición se considera elevada por la dependencia de registros manuales y por la ausencia previa de un mecanismo sistemático de validación.

El impacto es alto porque las existencias alimentan las decisiones de reposición. Un error puede provocar compras excesivas, faltantes y sugerencias incorrectas.

La valoración P3 es un juicio preliminar sobre la exposición a errores, no una frecuencia de incidentes medida. Debe revisarse con los propietarios.

### R2. Modificación no autorizada del historial

**Probabilidad inherente propuesta:** P2 — Media.  
**Impacto inherente:** I3 — Alto.  
**Resultado:** 6 — Riesgo alto.

En ausencia de controles de acceso, separación de funciones y registros de auditoría, una cuenta compartida o una persona con acceso directo podría modificar o eliminar movimientos sin dejar evidencia suficiente.

La probabilidad se estima media porque el escenario es posible, aunque no se han documentado incidentes que permitan considerarlo frecuente.

El impacto es alto: perder integridad en el historial afecta la trazabilidad, el cálculo de existencias, los indicadores y la capacidad de investigar modificaciones.

### R3. Indisponibilidad de la aplicación

**Probabilidad inherente propuesta:** P2 — Media.  
**Impacto inherente:** I3 — Alto.  
**Resultado:** 6 — Riesgo alto.

Sin procedimientos de contingencia, respaldos verificables ni recuperación documentada, una falla del servicio, del equipo o de la conectividad podría interrumpir el registro de movimientos y la consulta de información para abastecimiento.

La probabilidad se considera media debido a la dependencia tecnológica del sistema, sin asumir que las interrupciones sean frecuentes.

El impacto inherente es alto porque una caída prolongada podría impedir consultar saldos confiables, revisar alertas y preparar pedidos oportunamente.

### R4. Suplantación de proveedores

**Probabilidad inherente propuesta:** P2 — Media.  
**Impacto inherente:** I3 — Alto.  
**Resultado:** 6 — Riesgo alto.

Si se aceptan cambios de contacto o instrucciones de pedido sin verificar su autenticidad, un tercero podría hacerse pasar por un proveedor mediante mensajería o llamadas.

La probabilidad es media porque el intercambio de pedidos por canales de comunicación externos hace posible este escenario, aunque no existe evidencia de incidentes recurrentes en la empresa.

El impacto es alto porque el engaño podría provocar pedidos dirigidos a destinatarios incorrectos, pérdidas económicas o divulgación de información comercial.

### R5. Pérdida de información y respaldos

**Probabilidad inherente propuesta:** P2 — Media.  
**Impacto inherente:** I3 — Alto.  
**Resultado:** 6 — Riesgo alto.

En ausencia de copias independientes y restauraciones verificadas, una corrupción de datos, eliminación accidental o incidente de seguridad podría afectar tanto la base principal como los respaldos accesibles desde el mismo entorno.

La probabilidad se considera media: el escenario es técnicamente posible, pero no se dispone de estadísticas propias que demuestren una ocurrencia frecuente.

El impacto es alto porque la pérdida del historial dificultaría reconstruir existencias, movimientos, pedidos e indicadores de demanda.

### R6. Modificación accidental de reglas de reposición

**Probabilidad inherente propuesta:** P2 — Media.  
**Impacto inherente:** I2 — Medio.  
**Resultado:** 4 — Riesgo medio.

Si los umbrales o las reglas de cálculo pudieran modificarse sin revisión, pruebas ni historial de cambios, un error podría producir sugerencias de abastecimiento incorrectas.

La probabilidad es media porque la modificación accidental de parámetros es posible durante el mantenimiento del sistema.

El impacto se considera medio porque la sugerencia no ejecuta automáticamente una compra: el propietario conserva la decisión operativa y puede revisar las cantidades antes de aprobarlas.

## 3. Consolidación

| Riesgo | P inherente | I inherente | Nivel inherente | Residual propuesto en el taller |
|---|---|---|---|---|
| R1 | P3 | I3 | 9 — Alto | 6 — Alto |
| R2 | P2 | I3 | 6 — Alto | 3 — Medio |
| R3 | P2 | I3 | 6 — Alto | 4 — Medio |
| R4 | P2 | I3 | 6 — Alto | 6 — Alto |
| R5 | P2 | I3 | 6 — Alto | 3 — Medio |
| R6 | P2 | I2 | 4 — Medio | 2 — Bajo |

## 4. Interpretación y limitaciones

Las diferencias entre los niveles inherentes y residuales expresan el efecto esperado de los controles, no una reducción estadísticamente demostrada.

Especialmente:

- R1 conserva un riesgo residual alto porque las validaciones no detectan todos los saldos incorrectos.
- R4 conserva riesgo alto porque aprobar un pedido no verifica necesariamente la identidad del proveedor.
- R5 solo puede justificar el residual previsto cuando existan copias efectivamente segregadas y recuperables. La restauración local demostrada es una evidencia parcial.
- R3 requiere un simulacro operativo para validar la continuidad; las pruebas de n8n y de restauración aislada no equivalen a un RTO o RPO comprobado.

La aceptación de los riesgos residuales corresponde a los responsables del negocio. Esta evaluación debe revisarse si aparecen datos reales de incidentes, resultados de auditoría o cambios en los controles.

**Conclusión:** la evaluación proporciona una línea de análisis inherente para los seis riesgos existentes y permite compararla con los valores residuales del taller, sin afirmar que las reducciones proyectadas ya se hayan conseguido en la operación real.
