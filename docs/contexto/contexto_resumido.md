# Demanda360 en dos páginas

## La empresa

**Pinturas By-plus** es una tienda de pinturas y ferretería en Bogotá con unos 14 años de funcionamiento. Trabajan tres personas, dos de ellas propietarios. Venden pinturas de agua y aceite, esmaltes, lacas, selladores, barnices, solventes, aerosoles, brochas, lijas y herramientas. Entrevistamos a los dos propietarios el 12 de octubre de 2026.

## El problema

Los propietarios **sí cuentan la mercancía**, pero el cuaderno de ventas solo guarda el **total en pesos de cada día**, no cuántas unidades se vendieron de cada producto. Deciden qué comprar con su experiencia y su memoria. Resultado, según ellos: algunos productos se agotan (sellador catalizado, lacas brillantes, algunos esmaltes) y otros pasan meses guardados, a veces cerca de un año. No hay cifras medidas de pérdidas.

**Frase del problema:** By-plus no tiene registros de demanda por producto ni un análisis de rotación que respalde sus decisiones de compra.

## El proceso que estudiamos

**Planificación y generación de pedidos de abastecimiento:** se nota la necesidad de revisar → se cuenta → se decide qué y cuánto pedir → se hace la lista → se elige proveedor → se envía por WhatsApp o llamada → se espera respuesta → si hay disponibilidad se confirma; si no, se busca otro proveedor. La entrega tarda de 2 a 5 días (es la entrega, no el tiempo de respuesta).

## Fricciones (método MEDITA)

| Letra | Fricción |
|---|---|
| M · Manual | Conteos físicos para saber cuánto hay |
| I · Información | No hay ventas históricas por producto |
| E · Espera | Se depende de la respuesta del proveedor y del plazo de entrega |
| T · Trazabilidad | No hay seguimiento central de pedidos ni de agotamientos |
| D · Duplicidad (posible) | La lista se escribe y luego se vuelve a escribir en WhatsApp; falta confirmarlo |

## La solución: Demanda360

Una aplicación web sencilla para:

1. Registrar productos (cada uno con un código único, el SKU).
2. Registrar un conteo inicial y luego ventas, entradas de mercancía y ajustes.
3. Registrar cuánto pidió el cliente y cuánto se le entregó (para medir la demanda que no se atendió).
4. Ver existencias y el estado de cada producto: agotado, crítico, baja rotación, datos insuficientes o normal.
5. Avisar por correo cuando un producto llega a su nivel crítico (con n8n).
6. Sugerir cuánto pedir con una regla visible y preparar un borrador de pedido que **el propietario aprueba**.
7. Mostrar indicadores en Power BI.

**No tiene inteligencia artificial.** La IA queda como posible evolución futura, con sus riesgos éticos explicados.

**Regla de oro de la arquitectura:** Flask (la app) valida y guarda; PostgreSQL (la base de datos) es la única fuente de la verdad; n8n solo avisa; Power BI solo lee.

## Los 5 indicadores (KPI)

| KPI | Qué mide | Valor con datos simulados |
|---|---|---|
| 1. Referencias agotadas | % de productos con existencia 0 en el corte | 27 % (3 de 11) |
| 2. Demanda no atendida | % de unidades pedidas por clientes que no se pudieron entregar | 8,6 % (12 de 139) |
| 3. Baja rotación | % de productos con existencia y 0 a 2 ventas en 30 días | 50 % (5 de 10) |
| 4. Tiempo de confirmación del proveedor | Horas entre enviar el pedido y recibir respuesta | Sin línea base |
| 5. Confirmados con el primer proveedor | % de pedidos confirmados sin buscar otro proveedor | Sin línea base |

Las metas (−20 %, −20 %, −10 %) son provisionales frente a una línea base que todavía no existe.

## Seguridad, continuidad y ética (del taller)

- Basado en Calder y Watkins (2024) e ISO/IEC 27001 y 27002:2022. **By-plus no está certificada.**
- Controles que sí mostramos: SKU único, validación de cantidades, login, contraseñas cifradas, permisos por rol, aprobación del propietario, bitácora, ajustes justificados, claves fuera de GitHub, respaldo y restauración, datos personales mínimos y control de versiones.
- **RTO 4 horas y RPO 1 hora** son objetivos; solo reportamos lo que midamos en la prueba.
- El profesor nos dio 80/100 en el taller y pidió: matriz de riesgos completa (antes y después de controles), justificar cada puntaje y darle más impacto a la pérdida de la base de datos.
- Ética: registrar la demanda no atendida (si no, un producto agotado parece «sin demanda»), no castigar a proveedores con pocos datos, decir «datos insuficientes» cuando falten, y que el propietario siempre apruebe. Ley 1581 de 2012 sobre datos personales.

## Fechas

| Fecha | Qué |
|---|---|
| 12 oct | Entrevista a los propietarios |
| 13 oct | Entregable 1 (diagnóstico) |
| 4 nov | Taller de seguridad |
| 7–8 nov | Desarrollo intensivo |
| 9–10 nov | Integración, pruebas y documentación |
| **11 nov** | **Entrega final** |
