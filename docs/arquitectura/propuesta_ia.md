# Propuesta de IA · Demanda360

> Entregable 11 (automatización, analítica e IA). Separa lo que el MVP **implementa** de lo que se **propone** a futuro, con sus condiciones. Redactado por el Rol 1 a partir del código de la versión 1.0.

## 1. En una frase

**El MVP no usa inteligencia artificial.** Lo que automatiza son reglas fijas y transparentes. La IA queda como una evolución posible, que solo se justifica cuando haya meses de datos reales de Pinturas By-plus y que nunca reemplazaría la aprobación del propietario.

## 2. Qué está implementado (y por qué no es IA)

| Componente | Qué hace | Por qué no es IA |
| --- | --- | --- |
| Estado de cada producto | Agotado, crítico, datos insuficientes, baja rotación o normal | Reglas con umbrales fijos, en orden de prioridad |
| Cantidad sugerida | `máx(0, techo(demanda de 30 días × cobertura / 30 − saldo))` | Fórmula aritmética que se muestra con sus números en pantalla |
| Alerta de stock crítico (n8n) | Envía un correo cuando una venta cruza el umbral | Regla fija: saldo antes > umbral ≥ saldo después |
| KPI y Power BI | Cinco indicadores del mes | Analítica descriptiva: cuenta y promedia lo que ya pasó |

Ninguno de estos componentes aprende de los datos ni hace predicciones. Por eso cualquier resultado se puede explicar y recalcular a mano, como hizo el Rol 3 en Excel.

## 3. Qué no está implementado

- Pronóstico de demanda o cualquier modelo predictivo.
- Puntuación o ranking de proveedores.
- Envío automático de pedidos: el propietario aprueba cada uno.
- Análisis de conversaciones de WhatsApp o de mensajes de clientes y proveedores.
- Detección automática de ajustes de inventario inusuales.

## 4. Propuesta a futuro

### Fase 1 · Pronóstico de demanda por referencia

**Para qué:** que la cantidad sugerida considere la estacionalidad y la tendencia, no solo el promedio de los últimos 30 días.

**Condiciones para empezar:**

1. Varios meses de registros **reales** de By-plus; idealmente un año completo, para captar la estacionalidad. Hoy solo hay un mes simulado.
2. Una línea base medida con la regla actual, para comparar.
3. Que el pronóstico supere a la regla actual en una prueba con datos históricos (por ejemplo, con menor error promedio por referencia). Si no la supera, se mantiene la regla.

**Cómo se haría:** empezar con métodos simples y explicables, como promedios móviles o suavizamiento exponencial, antes de cualquier modelo complejo. La pantalla seguiría mostrando el cálculo y el propietario seguiría aprobando cada pedido.

### Fase 2 · Aviso de ajustes inusuales

**Para qué:** señalar ajustes de inventario fuera de lo normal (por tamaño o frecuencia) para que el propietario los revise.

**Límite:** solo avisa. No bloquea ajustes ni acusa a nadie. La decisión es siempre de una persona.

## 5. Condiciones éticas, ya resueltas en el MVP

| Riesgo | Por qué importa para una IA | Cómo lo deja preparado el MVP |
| --- | --- | --- |
| **Demanda subestimada** | Un producto agotado vende poco aunque lo pidan; un modelo entrenado solo con ventas aprendería a pedir menos | Se registra la **demanda no atendida** (lo solicitado menos lo entregado) |
| **Proveedores pequeños** | Un proveedor con poco historial podría parecer peor que uno con más registros | El MVP no puntúa proveedores, y separa «datos insuficientes» de bajo desempeño |
| **Privacidad** | Un modelo podría usar datos personales sin necesidad | No se guardan datos de clientes ni conversaciones (Ley 1581 de 2012); solo producto, cantidades y fechas |
| **Responsabilidad** | Una recomendación automática podría tratarse como una orden | El propietario aprueba cada pedido y queda registrado quién lo hizo |
| **Transparencia** | Un modelo de caja negra no se puede cuestionar | Cada sugerencia muestra su fórmula; una IA futura tendría que explicar sus razones igual |

## 6. Qué no se promete

- No se afirma que una IA mejoraría las ventas o reduciría los agotados: sin datos reales no se puede medir.
- No se propone reemplazar el criterio del propietario.
- La propuesta se puede revertir: si un modelo no funciona, se vuelve a la regla actual sin perder datos.
