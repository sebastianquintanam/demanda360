# CONTEXTO MAESTRO DEL PROYECTO DEMANDA360

## 1. Tu función

Actúa como arquitecto de software, desarrollador senior y mentor técnico de un equipo universitario de cuatro estudiantes de Ingeniería de Sistemas.

Necesitamos diseñar y desarrollar un MVP funcional de nuestro proyecto integrador llamado **Demanda360**, para la asignatura Fundamentos de Sistemas de Información de la Universidad EAN.

Docente: Diego Chinchilla.

Equipo:
- Brayan Felipe Álvarez Nieto.
- Olmer Carrillo.
- Andrés Sebastián Quintana Morales.
- Jhonatan Stiben Rey Velásquez.

La entrega final es el **11 de noviembre de 2026**.

Queremos trabajar intensivamente durante el 7 y 8 de noviembre, realizando integración, pruebas y documentación el 9 y 10.

El proyecto debe poder distribuirse entre cuatro desarrolladores trabajando simultáneamente mediante Git y GitHub.

No queremos sobreingeniería. Necesitamos una solución académica coherente, demostrable, segura, mantenible y realizable dentro del tiempo disponible.

Antes de generar grandes cantidades de código, analiza los requisitos, define la arquitectura, el modelo de datos, los contratos de integración y las tareas de los integrantes.

## 2. Contexto empresarial

Empresa: **Pinturas By-plus**.

Ubicación: Bogotá, Colombia.

Actividad: comercio minorista de pinturas y productos de ferretería.

Trayectoria aproximada: 14 años.

Trabajadores: tres personas, incluidos los dos propietarios.

Productos principales:
- Pinturas de agua y aceite.
- Esmaltes.
- Lacas.
- Selladores y selladores catalizados.
- Barnices.
- Solventes.
- Aerosoles.
- Brochas, lijas, herramientas y artículos de ferretería.

La investigación se basó en entrevistas realizadas a los dos propietarios el 12 de octubre de 2026 y evidencias comerciales del establecimiento.

### Cómo funciona actualmente

Los propietarios revisan físicamente las existencias y deciden qué comprar según su experiencia y lo que recuerdan de las ventas recientes.

El cuaderno de ventas registra principalmente el valor monetario total vendido diariamente. No existe un historial sistemático de unidades vendidas por SKU.

Conservan facturas de proveedores y realizan pedidos mediante WhatsApp, llamadas telefónicas o contacto directo.

Los tiempos habituales de entrega reportados son aproximadamente de dos a cinco días. Esta estimación corresponde a la entrega de mercancía, no al tiempo de respuesta del proveedor.

En determinados productos han ocurrido agotamientos, mientras que otros permanecen almacenados durante varios meses.

Los entrevistados mencionaron referencias como selladores catalizados, lacas brillantes y determinados esmaltes. Algunas referencias de baja rotación pueden permanecer almacenadas cerca de un año.

Estos datos proceden de declaraciones de los propietarios. No se cuenta con estadísticas verificadas de frecuencia de agotamientos, ventas perdidas o capital inmovilizado.

### Problema empresarial central

Pinturas By-plus no dispone de registros sistemáticos de demanda por producto ni de un análisis periódico de rotación que permita fundamentar sus decisiones de reposición.

El problema NO es que nunca realicen conteos: sí los hacen físicamente.

El problema tampoco consiste exclusivamente en consultar cuánto inventario existe.

Queremos mejorar la planificación de las compras mediante registros estructurados de demanda, existencias y solicitudes de clientes.

## 3. Alcance del proceso

Proceso seleccionado:

**Planificación y generación de pedidos de abastecimiento.**

Inicio: durante la operación habitual se identifica la necesidad de revisar existencias y evaluar la reposición.

Fin: el pedido queda confirmado con una fecha estimada de entrega o finaliza la revisión porque no se necesita comprar.

En el proceso actual:

1. Se identifica la necesidad de revisar las existencias.
2. Se realiza un conteo físico.
3. Se determinan productos y cantidades a solicitar.
4. Se decide si es necesario comprar.
5. Se prepara una lista de compra.
6. Se selecciona proveedor y marca.
7. Se envía la solicitud.
8. Se espera la respuesta.
9. Si existe disponibilidad, se confirma el pedido.
10. Si el proveedor no tiene disponibilidad, se consulta otro proveedor y se repite la solicitud.

Los propietarios indicaron que hasta ahora han conseguido los productos con alguno de sus proveedores.

No debemos inventar un escenario real de abandono definitivo del pedido.

El profesor sugirió incorporar un evento temporizador BPMN cuando el proveedor no responde. Su duración y comportamiento deben validarse; no podemos utilizar los dos a cinco días de entrega como tiempo de respuesta.

La recepción física, facturación, devoluciones y cambios de precios quedaron fuera del BPMN AS-IS delimitado.

El sistema digital podría registrar entradas posteriores para mantener actualizadas las existencias, pero debemos explicar que esto es una función del nuevo sistema y no una ampliación retroactiva del proceso diagnosticado.

## 4. Fricciones identificadas mediante MEDITA

La metodología enseñada en clase es:

- M: Manual.
- E: Espera.
- D: Duplicidad.
- I: Información.
- T: Trazabilidad.
- A: Actividad inútil.

Fricciones identificadas:

**Manual:** conteos físicos para conocer las existencias.

**Información:** ausencia de ventas históricas detalladas por referencia.

**Espera:** dependencia de la respuesta de proveedores y del posterior plazo de entrega.

**Trazabilidad:** falta de un seguimiento centralizado de pedidos y agotamientos.

**Duplicidad potencial:** posible transcripción repetida de la lista de compra cuando se pasa de una anotación a un mensaje de WhatsApp. Este caso debe validarse antes de declararlo como hecho confirmado.

No hay que inventar tiempos medidos ni fricciones no observadas.

## 5. Solución propuesta: Demanda360

Queremos desarrollar un sistema de información de apoyo a la planificación de abastecimiento.

Funciones principales:

1. Registrar productos y sus características.
2. Registrar un conteo físico inicial.
3. Registrar movimientos por producto, especialmente ventas y ajustes.
4. Registrar solicitudes de clientes, incluidas cantidades no atendidas.
5. Consultar existencias y productos críticos.
6. Analizar demanda histórica y rotación.
7. Calcular KPI.
8. Generar sugerencias sencillas de reposición.
9. Preparar borradores de pedidos.
10. Obtener aprobación del propietario antes de enviar un pedido.
11. Automatizar alertas mediante n8n.
12. Visualizar datos mediante Power BI.

La primera versión no necesita un modelo de inteligencia artificial.

Las recomendaciones de compra deben utilizar reglas transparentes y permitir revisión humana.

La interfaz visual se basará en las cuatro pantallas ya diseñadas en Figma:

- Dashboard.
- Registro.
- Análisis de demanda.
- Planificación de pedidos.

Figma es únicamente una referencia visual; sus pantallas no equivalen a funcionalidades implementadas.

## 6. Arquitectura tecnológica preferida

Tecnologías seleccionadas:

**Backend:** Python y Flask.

**Persistencia:** PostgreSQL.

**ORM:** SQLAlchemy o Flask-SQLAlchemy.

**Frontend:** HTML, CSS y JavaScript, preferiblemente con plantillas Flask/Jinja para reducir complejidad.

**Gráficas dentro de la aplicación:** Chart.js, si resulta necesario.

**Automatización:** n8n.

**Analítica empresarial:** Power BI.

**Infraestructura local:** Docker y Docker Compose.

**Control de versiones:** Git y GitHub.

**Pruebas:** pytest y pruebas de integración.

**Documentación:** README y diagramas Mermaid o equivalentes.

Desarrollo principal en Ubuntu Linux.

Power BI Desktop se utilizará desde un equipo Windows del grupo.

Preferimos PostgreSQL porque permite integración con n8n y Power BI y proporciona transacciones, restricciones, permisos y persistencia adecuados.

No queremos utilizar Excel como base central si PostgreSQL funciona.

Tampoco queremos incorporar Kubernetes, Terraform, servicios cloud, microservicios ni inteligencia artificial compleja para este MVP.

### Principio arquitectónico importante

Flask es responsable de validar y registrar los movimientos.

PostgreSQL es la fuente oficial de datos.

n8n se utiliza para notificaciones y automatizaciones.

Power BI consulta y visualiza información.

No queremos que Flask, n8n y Power BI mantengan cada uno saldos diferentes.

## 7. Modelo de datos inicial

Proponer un modelo relacional normalizado, con claves primarias, foráneas, índices y restricciones.

Entidades candidatas:

### usuarios
- id.
- nombre.
- identificador de acceso.
- hash de contraseña.
- rol.
- activo.

Roles mínimos:
- Propietario.
- Trabajador.

### productos
- id.
- sku único.
- nombre.
- categoría.
- marca.
- presentación.
- unidad de medida.
- costo de compra.
- precio de venta.
- umbral de reposición.
- activo.

Los SKU deben distinguir presentaciones diferentes, por ejemplo un galón y medio galón.

### conteos_fisicos
- id.
- producto_id.
- cantidad_contada.
- fecha_hora.
- usuario_responsable.
- observaciones.

### movimientos
- id único.
- producto_id.
- tipo de movimiento.
- cantidad.
- fecha_hora.
- responsable.
- identificador de origen.
- justificación.

Tipos iniciales:
- Existencia inicial.
- Venta.
- Entrada.
- Ajuste.

La cantidad disponible debe calcularse de forma coherente a partir de un conteo inicial verificado y movimientos posteriores.

No borrar movimientos para corregir errores: utilizar ajustes trazables.

Las ventas no pueden producir existencias negativas sin una decisión de negocio explícita.

### solicitudes_clientes
- id.
- producto_id.
- cantidad_solicitada.
- cantidad_entregada_inmediatamente.
- fecha_hora.
- estado.

Necesaria para calcular demanda no atendida.

Una solicitud no debe contabilizarse dos veces si el cliente vuelve posteriormente.

### proveedores
- id.
- nombre comercial.
- código.
- plazo estimado de entrega.
- activo.

Los contactos personales deben ser opcionales, mínimos y protegidos.

### pedidos
- id.
- proveedor_id.
- estado.
- fecha_creacion.
- fecha_envio.
- fecha_respuesta.
- usuario_creador.
- usuario_aprobador.
- fecha_aprobacion.

Estados sugeridos:
- Borrador.
- Aprobado.
- Enviado.
- Confirmado.
- Cancelado.

### pedido_detalles
- id.
- pedido_id.
- producto_id.
- cantidad_solicitada.

### auditoria
- id.
- usuario.
- acción.
- entidad.
- identificador_entidad.
- fecha_hora.
- detalle mínimo del cambio.

### eventos_automatizacion
- id único de evento.
- tipo.
- fecha.
- estado de notificación.
- intentos.

Esta última tabla puede simplificarse si el tiempo no alcanza, pero necesitamos evitar enviar alertas duplicadas.

Solicito que revises si estas tablas están bien normalizadas y cuáles son imprescindibles para el MVP.

## 8. KPI requeridos

En la primera entrega se definieron tres KPI.

Para la fase final el material de clase solicita al menos cinco.

### KPI 1. Porcentaje de referencias agotadas

Fórmula:

(Referencias con existencia verificada igual a cero / Referencias monitoreadas con conteo verificado) × 100.

Debe utilizar un corte temporal explícito.

No interpretar la falta de conteo como existencia cero.

Objetivo: mejorar la disponibilidad.

Meta preliminar original: reducción relativa del 20 % frente a una línea base futura validada.

### KPI 2. Porcentaje de demanda no atendida inmediatamente

Fórmula:

(Unidades solicitadas no entregadas inmediatamente / Total de unidades solicitadas) × 100.

Se requieren registros de solicitudes y cantidades entregadas.

No duplicar la demanda cuando un cliente regresa posteriormente.

Meta preliminar: reducción relativa del 20 % frente a la línea base.

### KPI 3. Porcentaje de referencias de baja rotación

Fórmula:

(Referencias clasificadas con baja rotación / Referencias monitoreadas con información completa) × 100.

Regla provisional del prototipo:

Referencias con existencias positivas y entre cero y dos unidades vendidas durante 30 días completos.

No es una regla universal; debe validarse por familia.

Cuando falten datos debe aparecer "Datos insuficientes".

Meta preliminar: reducir un 10 % relativo después de obtener una línea base.

### KPI 4. Tiempo promedio de confirmación del proveedor

Medir tiempo entre solicitud enviada y respuesta de confirmación.

Requiere guardar marcas de tiempo.

La línea base no está disponible.

### KPI 5. Porcentaje de pedidos confirmados con el primer proveedor

Medir el porcentaje de pedidos confirmados sin necesidad de consultar un proveedor alternativo.

Definir claramente el denominador y registrar la secuencia de consultas.

La línea base no está disponible.

Cada KPI debe tener:
- Nombre.
- Objetivo empresarial.
- Fórmula.
- Unidad.
- Fuente de información.
- Frecuencia.
- Meta.
- Responsable.
- Interpretación.
- Reglas de calidad del dato.

No presentar metas provisionales como logros reales.

## 9. Datos requeridos del almacén

Para el piloto necesitamos un conjunto pequeño de 10 a 15 referencias representativas.

Datos a recopilar, preferiblemente con información verificada:

- SKU o identificador.
- Nombre del producto.
- Categoría.
- Marca.
- Presentación.
- Unidad de medida.
- Existencia física.
- Fecha del conteo.
- Costo unitario.
- Precio de venta.
- Proveedor habitual.
- Plazo de entrega estimado.
- Umbral de reposición propuesto.
- Productos con agotamientos frecuentes.
- Productos que permanecen mucho tiempo almacenados.

No disponemos de ventas históricas completas por SKU.

Por tanto, cualquier historial de 30 días utilizado para demostrar tendencias será SIMULADO y deberá identificarse como tal.

Podemos tener dos conjuntos distintos:

**Datos levantados del negocio:** solo información verificada y autorizada.

**Datos de demostración:** registros sintéticos para probar el sistema y calcular KPI.

No mezclar ambos sin indicar su origen.

Los datos sintéticos deben tener coherencia temporal y permitir demostrar agotamientos, baja rotación, solicitudes no atendidas y pedidos.

## 10. Seguridad de la información y normas ISO

El profesor indicó que el taller de seguridad debe reflejarse directamente en el proyecto integrador.

La base conceptual procede del libro:

Calder y Watkins, IT Governance: An International Guide to Data Security and ISO 27001/ISO 27002, octava edición, 2024.

Normas de referencia:
- ISO/IEC 27001:2022.
- ISO/IEC 27002:2022.

Es importante distinguir ambas:

ISO 27001 establece los requisitos para gestionar la seguridad mediante un SGSI.

ISO 27002 orienta sobre los controles de seguridad.

No afirmar que Pinturas By-plus está certificada.

### Controles mínimos que sí queremos demostrar

1. Validación de SKU único.
2. Validación de cantidades y unidades.
3. Autenticación de usuarios.
4. Contraseñas almacenadas mediante hash seguro.
5. Permisos según rol.
6. Aprobación del propietario antes de confirmar o enviar pedidos.
7. Bitácora de operaciones relevantes.
8. Registro y justificación de ajustes.
9. Protección de las credenciales mediante variables de entorno.
10. Respaldo y restauración de PostgreSQL.
11. Minimización de datos personales.
12. Control de versiones mediante Git.

No almacenar contraseñas en texto plano ni publicar datos sensibles en GitHub.

No exponer PostgreSQL directamente a Internet.

Las validaciones de permisos deben ejecutarse en el backend, no solamente ocultar botones.

### Riesgos estudiados

Se identificaron seis activos:

- Catálogo y existencias.
- Historial de movimientos.
- Aplicación y disponibilidad.
- Pedidos y contactos de proveedores.
- Respaldos.
- Reglas de reposición.

Los escenarios incluyen errores de datos, modificaciones no autorizadas, interrupciones, suplantación de proveedores, pérdida de información y cambios incorrectos de reglas.

El profesor observó que la pérdida grave de la base de datos merece una valoración de impacto mayor.

Debemos diseñar una matriz de riesgos con escala consistente y justificar cada puntaje de probabilidad e impacto antes y después del tratamiento.

No inventar probabilidades comprobadas.

No confundir una reducción hipotética con la eficacia demostrada de un control.

Para la defensa final hay que mostrar la matriz completa y explicar los valores.

## 11. Continuidad del negocio

En el taller propusimos:

**RTO: 4 horas.**

Objetivo de recuperar la consulta y el registro digital durante la misma jornada.

**RPO: 1 hora.**

Objetivo de limitar la antigüedad de los datos que podrían perderse y permitir la reconstrucción mediante comprobantes y registros de contingencia.

Ambos valores son objetivos académicos pendientes de comprobar.

Implementar al menos un procedimiento documentado de respaldo de PostgreSQL y una restauración en una base de pruebas.

Registrar:
- Fecha del respaldo.
- Resultado.
- Fecha de restauración.
- Duración.
- Registros verificados.

La persistencia de un volumen Docker NO equivale a tener un respaldo.

Si el servicio falla, la tienda puede continuar temporalmente mediante registros manuales, con folios únicos, para conciliarlos posteriormente.

## 12. Ética e inteligencia artificial

No desarrollar IA predictiva como requisito obligatorio del MVP.

La IA se considera una evolución futura.

Riesgos identificados:

### Demanda subestimada

Cuando un producto está agotado registra pocas ventas, aunque los clientes sigan solicitándolo.

Un modelo que solo utilice ventas podría recomendar reponer menos.

Por eso debemos registrar demanda no atendida.

### Proveedores pequeños

Un proveedor con poco historial digital podría recibir una evaluación inferior frente a otro con mayor cantidad de registros, aunque ambos ofrezcan condiciones adecuadas.

Debemos distinguir entre bajo desempeño y datos insuficientes.

### Privacidad

No enviar conversaciones completas de clientes o proveedores a herramientas de IA.

Utilizar únicamente los datos necesarios para analizar demanda.

### Responsabilidad

Los propietarios conservan la aprobación de las compras.

El sistema debe informar las razones de las recomendaciones y permitir correcciones.

En Colombia considerar el tratamiento de datos personales bajo la Ley 1581 de 2012.

## 13. Automatización seleccionada para n8n

La automatización principal será:

**Venta registrada → saldo actualizado → stock crítico detectado → aviso al propietario.**

Flujo esperado:

1. Un trabajador registra una venta en Flask.
2. El backend valida los datos.
3. PostgreSQL guarda el movimiento mediante una transacción.
4. Se calcula el saldo disponible.
5. Se comprueba si el producto alcanzó su umbral.
6. Flask genera un evento con ID único.
7. n8n recibe el evento mediante un webhook protegido.
8. n8n procesa la alerta y envía una notificación de prueba por correo.
9. Se conserva evidencia del resultado.
10. Power BI refleja el movimiento al actualizar sus datos.

n8n no debe convertirse en la fuente oficial del inventario.

Si falla la notificación, la venta ya registrada no debe perderse.

Evitar alertas duplicadas y controlar reintentos.

El envío de un pedido debe requerir aprobación humana.

## 14. Power BI

Crear un dashboard académico utilizando PostgreSQL como fuente de datos o una exportación controlada para la demostración.

Preferimos una conexión de solo lectura.

Pantallas o secciones sugeridas:

- Resumen general.
- Disponibilidad.
- Demanda.
- Baja rotación.
- Pedidos y proveedores.

Mostrar cinco KPI cuando existan los datos necesarios.

Diferenciar datos simulados y reales.

No presentar el dashboard como una prueba de reducción de pérdidas económicas.

Si PostgreSQL funciona en un computador diferente al utilizado para Power BI, proponer una alternativa segura de integración sin abrir la base de datos a Internet.

## 15. Organización del equipo

Dividir el desarrollo en cuatro responsabilidades.

### Brayan — Backend y PostgreSQL

- Configuración de Flask.
- Modelos de base de datos.
- API.
- Transacciones de movimientos.
- Reglas de validación.
- Cálculo de existencias.
- Integración general.

### Olmer — Frontend

- Pantallas basadas en Figma.
- Formularios.
- Catálogo.
- Registro de ventas.
- Visualización de productos críticos.
- Consumo de la API.

### Andrés Sebastián — Datos y Power BI

- Datos simulados coherentes.
- Diccionario de datos.
- Consultas SQL de KPI.
- Dashboards.
- Verificación matemática de los indicadores.

### Jhonatan — n8n, pruebas y seguridad

- Automatización.
- Alertas.
- Pruebas de integración.
- Controles de acceso.
- Evidencias de seguridad.
- Respaldo y restauración con apoyo de backend.

Ninguna persona debe modificar los mismos archivos principales simultáneamente sin coordinación.

## 16. Git y GitHub

Utilizar un repositorio privado común.

Rama estable: main.

Ramas propuestas:
- feature/backend.
- feature/frontend.
- feature/analytics.
- feature/automation.

Utilizar commits pequeños y pull requests.

No modificar directamente main durante el trabajo habitual.

Cada integrante debe realizar sus pruebas antes de integrar.

Mantener un .gitignore apropiado.

No subir:
- .env.
- Contraseñas.
- Bases de datos reales.
- Datos bancarios.
- Archivos de recuperación.
- Capturas sin censurar.

Guardar evidencias de avances en una carpeta docs/evidencias.

## 17. Estructura inicial del repositorio

demanda360/

  backend/
    app/
      models/
      routes/
      services/
      templates_config/
    tests/
    requirements.txt
    run.py

  frontend/
    templates/
    static/
      css/
      js/
      img/

  database/
    sql/
    seeds/
    backups_ejemplo/

  analytics/
    powerbi/
    consultas/
    datos_demo/

  automation/
    workflows/
    evidencias/

  docs/
    arquitectura/
    bpmn/
    requerimientos/
    seguridad/
    evidencias/

  compose.yaml
  .env.example
  .gitignore
  README.md

Puedes proponer una estructura más sencilla si aporta claridad, pero debes explicar por qué.

Los respaldos reales y archivos sensibles no deben almacenarse dentro del repositorio.

## 18. Contrato de API inicial

Necesitamos definir y documentar rutas comunes para que frontend, backend, analítica y automatización trabajen en paralelo.

Propuesta inicial:

GET /api/health

GET /api/productos

POST /api/productos

GET /api/productos/{id}

POST /api/conteos

POST /api/movimientos

POST /api/solicitudes

GET /api/dashboard

GET /api/analisis/rotacion

GET /api/pedidos

POST /api/pedidos

POST /api/pedidos/{id}/aprobar

Estas rutas son propuestas, no implementaciones existentes.

Antes de programar, define formatos JSON, códigos HTTP, validaciones, errores y ejemplos de respuesta.

El frontend debe poder trabajar con mocks mientras el backend se desarrolla.

Los errores técnicos no deben revelar contraseñas ni información interna.

## 19. Alcance mínimo obligatorio del MVP

Prioridades P0:

1. PostgreSQL funcionando.
2. Flask conectado.
3. Catálogo con SKU único.
4. Conteo inicial de productos.
5. Registro de ventas y movimientos.
6. Consulta de existencias.
7. Un dashboard con indicadores básicos.
8. Alerta n8n demostrable.
9. Control básico de acceso.
10. Prueba de respaldo y restauración.

Prioridades P1:

1. Solicitudes no atendidas.
2. KPI completos.
3. Análisis de baja rotación.
4. Borradores de compra.
5. Aprobación de pedidos.
6. Dashboard de Power BI completo.
7. Registro de auditoría ampliado.

Prioridades P2:

1. Inteligencia artificial predictiva.
2. Integración oficial de WhatsApp.
3. Envío totalmente automático de pedidos.
4. Servicios cloud.
5. Funciones avanzadas multiempresa.

La prioridad P0 es necesaria para demostrar el sistema. No debemos perderla por intentar finalizar antes P2.

## 20. Pruebas y criterios de aceptación

El MVP debe demostrar al menos:

- Crear un producto válido.
- Rechazar un SKU duplicado.
- Rechazar una cantidad inválida.
- Registrar un conteo inicial.
- Registrar una venta.
- Comprobar que el saldo cambia correctamente.
- Impedir cambios no autorizados.
- Generar una alerta por stock crítico.
- Mostrar el movimiento en la fuente de datos.
- Consultar un indicador calculado.
- Ejecutar un respaldo.
- Restaurar en una base independiente.
- Consultar el registro de una operación.

Utilizar datos simulados para las pruebas.

No afirmar que RTO y RPO se cumplen sin medirlos.

## 21. Entregables académicos a integrar

El profesor indicó que todo debe aparecer reflejado en el proyecto final:

1. Caracterización de Pinturas By-plus.
2. Problema empresarial.
3. BPMN AS-IS.
4. Diagnóstico de fricciones MEDITA.
5. BPMN TO-BE justificado.
6. Requerimientos funcionales y no funcionales.
7. Modelo conceptual de datos.
8. KPI.
9. Dashboard.
10. Arquitectura del sistema de información.
11. Automatización, analítica y posible evolución con IA.
12. Matriz de riesgos.
13. Seguridad ISO 27001/27002.
14. Continuidad del negocio.
15. Ética y protección de datos.
16. Evidencias del prototipo.
17. Conclusiones y siguientes pasos.

La documentación debe distinguir entre:
- Funcionalidad implementada.
- Funcionalidad demostrada con simulación.
- Propuesta futura.

## 22. Lo que necesito que hagas primero

No generes una aplicación completa de golpe.

Primero necesito que:

1. Analices la viabilidad del MVP con cuatro personas.
2. Identifiques dependencias y riesgos de integración.
3. Propongas la arquitectura final más simple.
4. Definas el modelo de datos mínimo.
5. Definas el contrato inicial de API con ejemplos JSON.
6. Propongas la estructura exacta del repositorio.
7. Dividas las tareas en cuatro ramas paralelas.
8. Indiques qué archivos son responsabilidad de cada integrante.
9. Establezcas criterios de aceptación por módulo.
10. Propongas un plan intensivo hasta el 11 de noviembre.

Después de acordar esos contratos, ayúdanos a crear el esqueleto del proyecto y los prompts específicos para cada integrante.

Trabaja paso a paso y explica los comandos de Linux, Docker, PostgreSQL, Flask y Git.

No inventes resultados empresariales, controles implementados ni mediciones históricas.

La prioridad es un sistema demostrable, coherente con el diagnóstico y con los requisitos académicos.

# FIN DEL CONTEXTO MAESTRO