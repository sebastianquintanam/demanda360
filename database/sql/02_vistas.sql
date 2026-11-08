-- =============================================================================
-- Demanda360 · Cálculos oficiales: saldo, estado, KPI y vistas de exportación
-- PostgreSQL 16 · Se carga después de 01_schema.sql. Se puede volver a correr
-- sin borrar datos (todo es DROP IF EXISTS + CREATE):
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < database/sql/02_vistas.sql
--
-- Una sola definición para todos: Flask (dashboard y API), Power BI (CSV) y la
-- verificación en Excel leen estas funciones y vistas. Si una cifra no cuadra,
-- se corrige AQUÍ, nunca en el tablero ni en la pantalla.
--
-- FECHA DE CORTE (decisión aprobada el 8 nov 2026)
--   Los KPI y la rotación se calculan sobre los 30 días que terminan el día de
--   corte, inclusive, en hora de Bogotá: [corte − 29 días 00:00, corte + 1 día 00:00).
--   Con el corte por defecto (2026-09-30) el periodo es del 1 al 30 de septiembre
--   hasta las 23:59:59.999. Se usa "< 1 de octubre 00:00" para no perder registros
--   con fracciones de segundo.
--   El corte se cambia sin tocar SQL:
--     · por sesión:  SET demanda360.corte = '2026-10-31';
--     · por base:    ALTER DATABASE demanda360 SET demanda360.corte = '2026-10-31';
--   Las funciones fn_* reciben el corte como parámetro (Flask lo pasa explícito).
--
-- SALDO
--   Saldo = último conteo + entradas − ventas ± ajustes posteriores a ese conteo.
--   Sin conteo → NULL ("Sin conteo"), nunca 0. Un movimiento con la misma
--   fecha_hora que el conteo se considera ya incluido en el conteo.
--   · Saldo al corte: solo lo registrado antes del límite del corte (KPI 1, CSV).
--   · Saldo actual:   todo lo registrado (pantallas en vivo: una venta de hoy
--     cambia el saldo y el estado, pero no mueve los KPI de septiembre).
--
-- CLIENTE QUE REGRESA (solicitud_previa_id)
--   Su atención queda registrada y enlazada a la original (la venta necesita una
--   atención y las solicitudes son de solo inserción), pero NO suma demanda:
--   se excluye de lo solicitado y de lo no atendido. El faltante de la atención
--   original se conserva. Sus unidades sí cuentan como vendidas (salieron del inventario).
-- =============================================================================

SET client_encoding = 'UTF8';
SET client_min_messages = warning;  -- sin avisos de "no existe" al recargar

-- Primero las vistas (dependen de las funciones)
DROP VIEW IF EXISTS
  vw_kpi_primer_proveedor, vw_kpi_respuesta, vw_kpi_rotacion, vw_kpi_demanda, vw_kpi_agotadas,
  vw_kpi_resumen, vw_pedidos, vw_solicitudes, vw_ventas_diarias, vw_inventario_actual,
  vw_sugeridos, vw_estado_productos, vw_saldos
  CASCADE;

DROP FUNCTION IF EXISTS fn_kpi_resumen(date) CASCADE;
DROP FUNCTION IF EXISTS fn_sugeridos(date, timestamptz, integer) CASCADE;
DROP FUNCTION IF EXISTS fn_estado_productos(date, timestamptz) CASCADE;
DROP FUNCTION IF EXISTS fn_metricas_periodo(date) CASCADE;
DROP FUNCTION IF EXISTS fn_saldos(timestamptz) CASCADE;
DROP FUNCTION IF EXISTS fn_limite_corte(date) CASCADE;
DROP FUNCTION IF EXISTS fn_corte() CASCADE;
DROP FUNCTION IF EXISTS fn_origen_datos() CASCADE;

-- -----------------------------------------------------------------------------
-- Parámetros
-- -----------------------------------------------------------------------------
CREATE FUNCTION fn_corte()
RETURNS date
LANGUAGE sql STABLE
AS $$
  -- 2026-09-30: fin del mes simulado. Ver encabezado para cambiarlo.
  SELECT COALESCE(NULLIF(current_setting('demanda360.corte', true), '')::date, DATE '2026-09-30');
$$;
COMMENT ON FUNCTION fn_corte() IS 'Corte vigente de los KPI: demanda360.corte o 2026-09-30.';

CREATE FUNCTION fn_origen_datos()
RETURNS text
LANGUAGE sql STABLE
AS $$
  -- Una base con datos verificados del negocio (demanda360_piloto) pondría otro valor
  SELECT COALESCE(NULLIF(current_setting('demanda360.origen_datos', true), ''), 'SIMULADO');
$$;

CREATE FUNCTION fn_limite_corte(p_corte date)
RETURNS timestamptz
LANGUAGE sql IMMUTABLE
AS $$
  -- Primer instante DESPUÉS del día de corte, en hora de Bogotá (límite exclusivo)
  SELECT ((p_corte + 1)::timestamp AT TIME ZONE 'America/Bogota');
$$;
COMMENT ON FUNCTION fn_limite_corte(date) IS 'corte + 1 día a las 00:00 de Bogotá. Todo periodo se filtra con fecha_hora < este valor.';

-- -----------------------------------------------------------------------------
-- Saldo por producto hasta un instante (exclusivo)
-- -----------------------------------------------------------------------------
CREATE FUNCTION fn_saldos(p_hasta timestamptz)
RETURNS TABLE (
  producto_id       bigint,
  saldo             integer,
  ultimo_conteo_en  timestamptz,
  primer_conteo_en  timestamptz
)
LANGUAGE sql STABLE
AS $$
  WITH ultimo AS (
    SELECT DISTINCT ON (c.producto_id) c.producto_id, c.cantidad_contada, c.fecha_hora
    FROM conteos_fisicos c
    WHERE c.fecha_hora < p_hasta
    ORDER BY c.producto_id, c.fecha_hora DESC, c.id DESC
  ),
  primero AS (
    SELECT c.producto_id, min(c.fecha_hora) AS fecha_hora
    FROM conteos_fisicos c
    WHERE c.fecha_hora < p_hasta
    GROUP BY c.producto_id
  ),
  despues AS (
    SELECT u.producto_id,
           sum(CASE m.tipo WHEN 'VENTA' THEN -m.cantidad ELSE m.cantidad END) AS neto
    FROM ultimo u
    JOIN movimientos m ON m.producto_id = u.producto_id
                      AND m.fecha_hora > u.fecha_hora
                      AND m.fecha_hora < p_hasta
    GROUP BY u.producto_id
  )
  SELECT p.id,
         (u.cantidad_contada + COALESCE(d.neto, 0))::integer,
         u.fecha_hora,
         pr.fecha_hora
  FROM productos p
  LEFT JOIN ultimo u ON u.producto_id = p.id
  LEFT JOIN primero pr ON pr.producto_id = p.id
  LEFT JOIN despues d ON d.producto_id = p.id;
$$;
COMMENT ON FUNCTION fn_saldos(timestamptz) IS 'Saldo calculado (nunca guardado). NULL = sin conteo. Para el saldo actual: fn_saldos(''infinity'').';

-- -----------------------------------------------------------------------------
-- Ventas y demanda de los 30 días que terminan en el corte
-- -----------------------------------------------------------------------------
CREATE FUNCTION fn_metricas_periodo(p_corte date)
RETURNS TABLE (
  producto_id       bigint,
  vendidas_30d      integer,
  demanda_30d       integer,
  no_atendidas_30d  integer,
  atenciones_30d    integer
)
LANGUAGE sql STABLE
AS $$
  WITH limites AS (
    SELECT fn_limite_corte(p_corte) - interval '30 days' AS desde, fn_limite_corte(p_corte) AS hasta
  ),
  ventas AS (
    SELECT m.producto_id, sum(m.cantidad) AS vendidas
    FROM movimientos m, limites l
    WHERE m.tipo = 'VENTA' AND m.fecha_hora >= l.desde AND m.fecha_hora < l.hasta
    GROUP BY m.producto_id
  ),
  demanda AS (
    -- El cliente que regresa no suma demanda (ver encabezado)
    SELECT s.producto_id,
           sum(s.cantidad_solicitada) AS solicitada,
           sum(s.cantidad_solicitada - s.cantidad_entregada) AS no_atendida,
           count(*) AS atenciones
    FROM solicitudes_clientes s, limites l
    WHERE s.solicitud_previa_id IS NULL
      AND s.fecha_hora >= l.desde AND s.fecha_hora < l.hasta
    GROUP BY s.producto_id
  )
  SELECT p.id,
         COALESCE(v.vendidas, 0)::integer,
         COALESCE(d.solicitada, 0)::integer,
         COALESCE(d.no_atendida, 0)::integer,
         COALESCE(d.atenciones, 0)::integer
  FROM productos p
  LEFT JOIN ventas v ON v.producto_id = p.id
  LEFT JOIN demanda d ON d.producto_id = p.id;
$$;

-- -----------------------------------------------------------------------------
-- Estado por producto
--   p_corte: periodo de rotación y días con registro
--   p_hasta: instante del saldo (fn_limite_corte(p_corte) para el corte; 'infinity' para hoy)
-- Orden (el primero que se cumple): Sin conteo → Agotado → Crítico →
-- Datos insuficientes (< 30 días desde el primer conteo) → Baja rotación
-- (0 a 2 vendidas en 30 días) → Normal.
-- -----------------------------------------------------------------------------
CREATE FUNCTION fn_estado_productos(p_corte date, p_hasta timestamptz)
RETURNS TABLE (
  producto_id        bigint,
  saldo              integer,
  umbral_reposicion  integer,
  primer_conteo_en   timestamptz,
  ultimo_conteo_en   timestamptz,
  dias_con_registro  integer,
  vendidas_30d       integer,
  demanda_30d        integer,
  no_atendidas_30d   integer,
  demanda_diaria     numeric,
  cobertura_dias     integer,
  estado             varchar
)
LANGUAGE sql STABLE
AS $$
  WITH base AS (
    SELECT p.id, p.umbral_reposicion, s.saldo, s.primer_conteo_en, s.ultimo_conteo_en,
           -- Días de calendario (Bogotá) desde el primer conteo hasta el corte, inclusive
           CASE WHEN s.primer_conteo_en IS NULL THEN NULL
                ELSE GREATEST(0, p_corte - (s.primer_conteo_en AT TIME ZONE 'America/Bogota')::date + 1)
           END AS dias,
           m.vendidas_30d, m.demanda_30d, m.no_atendidas_30d
    FROM productos p
    JOIN fn_saldos(p_hasta) s ON s.producto_id = p.id
    JOIN fn_metricas_periodo(p_corte) m ON m.producto_id = p.id
  )
  SELECT b.id,
         b.saldo,
         b.umbral_reposicion,
         b.primer_conteo_en,
         b.ultimo_conteo_en,
         b.dias,
         b.vendidas_30d,
         b.demanda_30d,
         b.no_atendidas_30d,
         CASE WHEN b.dias >= 30 THEN round(b.demanda_30d / 30.0, 2) END,
         -- Cobertura informativa: días que alcanza el saldo al ritmo de demanda (piso)
         CASE WHEN b.dias >= 30 AND b.saldo IS NOT NULL AND b.demanda_30d > 0
              THEN (GREATEST(b.saldo, 0) * 30) / b.demanda_30d END,
         (CASE
            WHEN b.saldo IS NULL                 THEN 'SIN_CONTEO'
            WHEN b.saldo <= 0                    THEN 'AGOTADO'
            WHEN b.saldo <= b.umbral_reposicion  THEN 'CRITICO'
            WHEN b.dias < 30                     THEN 'DATOS_INSUFICIENTES'
            WHEN b.vendidas_30d <= 2             THEN 'BAJA_ROTACION'
            ELSE 'NORMAL'
          END)::varchar
  FROM base b;
$$;

-- -----------------------------------------------------------------------------
-- Cantidad sugerida (P1) · regla versión 1
--   sugerido = máx(0, techo(demanda diaria × cobertura − saldo))
--   demanda diaria = (entregadas + no atendidas en 30 días) / 30
--   Con datos insuficientes o sin conteo: NULL (cantidad manual del propietario)
-- -----------------------------------------------------------------------------
CREATE FUNCTION fn_sugeridos(p_corte date, p_hasta timestamptz, p_cobertura integer)
RETURNS TABLE (
  producto_id       bigint,
  saldo             integer,
  demanda_diaria    numeric,
  cobertura_dias    integer,
  sugerido          integer,
  formula           text,
  regla_version     integer
)
LANGUAGE sql STABLE
AS $$
  SELECT e.producto_id,
         e.saldo,
         e.demanda_diaria,
         p_cobertura,
         CASE WHEN e.saldo IS NOT NULL AND e.dias_con_registro >= 30
              THEN GREATEST(0, ceil((e.demanda_30d * p_cobertura)::numeric / 30 - e.saldo))::integer
         END,
         CASE
           WHEN e.saldo IS NULL THEN 'Sin conteo: cantidad manual del propietario'
           WHEN e.dias_con_registro < 30 THEN
             format('Datos insuficientes (%s días de registros desde %s): cantidad manual del propietario',
                    e.dias_con_registro,
                    extract(day FROM e.primer_conteo_en AT TIME ZONE 'America/Bogota')::int || ' ' ||
                    (ARRAY['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'])
                      [extract(month FROM e.primer_conteo_en AT TIME ZONE 'America/Bogota')::int])
           WHEN ceil((e.demanda_30d * p_cobertura)::numeric / 30 - e.saldo) > 0 THEN
             format('techo((%s + %s) / 30 × %s − %s) = %s',
                    e.demanda_30d - e.no_atendidas_30d, e.no_atendidas_30d, p_cobertura, e.saldo,
                    ceil((e.demanda_30d * p_cobertura)::numeric / 30 - e.saldo))
           ELSE
             format('máx(0, techo((%s + %s) / 30 × %s − %s)) = 0',
                    e.demanda_30d - e.no_atendidas_30d, e.no_atendidas_30d, p_cobertura, e.saldo)
         END,
         1
  FROM fn_estado_productos(p_corte, p_hasta) e;
$$;

-- -----------------------------------------------------------------------------
-- KPI 1 a 5 de un corte (una fila por KPI)
-- -----------------------------------------------------------------------------
CREATE FUNCTION fn_kpi_resumen(p_corte date)
RETURNS TABLE (
  corte          date,
  periodo_desde  date,
  periodo_hasta  date,
  codigo         varchar,
  nombre         varchar,
  valor          numeric,
  unidad         varchar,
  numerador      numeric,
  denominador    integer,
  detalle        text,
  mejor_si       varchar,
  origen_datos   text
)
LANGUAGE sql STABLE
AS $$
  WITH lim AS (
    SELECT fn_limite_corte(p_corte) - interval '30 days' AS desde, fn_limite_corte(p_corte) AS hasta
  ),
  est AS (
    SELECT e.* FROM fn_estado_productos(p_corte, fn_limite_corte(p_corte)) e
    JOIN productos p ON p.id = e.producto_id AND p.activo
  ),
  k1 AS (
    -- Sin conteo no es cero: queda fuera del denominador
    SELECT count(*) FILTER (WHERE saldo <= 0) AS num, count(*) FILTER (WHERE saldo IS NOT NULL) AS den
    FROM est
  ),
  k2 AS (
    SELECT COALESCE(sum(no_atendidas_30d), 0) AS num, COALESCE(sum(demanda_30d), 0) AS den FROM est
  ),
  k3 AS (
    -- Menos de 30 días = datos insuficientes, fuera del denominador
    SELECT count(*) FILTER (WHERE saldo > 0 AND dias_con_registro >= 30 AND vendidas_30d <= 2) AS num,
           count(*) FILTER (WHERE saldo IS NOT NULL AND dias_con_registro >= 30) AS den,
           count(*) FILTER (WHERE saldo IS NOT NULL AND dias_con_registro < 30) AS insuficientes
    FROM est
  ),
  k4 AS (
    -- Horas de respuesta de los pedidos enviados en el periodo; sin respuesta se cuentan aparte
    SELECT COALESCE(sum(extract(epoch FROM (pe.fecha_respuesta - pe.fecha_envio)) / 3600.0)
                    FILTER (WHERE pe.fecha_respuesta < l.hasta), 0) AS horas,
           count(*) FILTER (WHERE pe.fecha_respuesta < l.hasta) AS con_respuesta,
           count(*) FILTER (WHERE pe.fecha_respuesta IS NULL OR pe.fecha_respuesta >= l.hasta) AS sin_respuesta
    FROM pedidos pe, lim l
    WHERE pe.fecha_envio >= l.desde AND pe.fecha_envio < l.hasta
  ),
  k5 AS (
    -- Cada cadena de reintentos termina en a lo sumo un confirmado: se cuenta una vez
    SELECT count(*) FILTER (WHERE pe.numero_intento = 1) AS num, count(*) AS den
    FROM pedidos pe, lim l
    WHERE pe.estado = 'CONFIRMADO' AND pe.fecha_respuesta >= l.desde AND pe.fecha_respuesta < l.hasta
  ),
  filas AS (
    SELECT 1 AS orden, 'KPI1'::varchar AS codigo, 'Referencias agotadas'::varchar AS nombre,
           CASE WHEN k1.den > 0 THEN round(k1.num * 100.0 / k1.den, 1) END AS valor, '%'::varchar AS unidad,
           k1.num::numeric AS numerador, k1.den::integer AS denominador,
           format('%s de %s referencias con conteo', k1.num, k1.den) AS detalle, 'menor'::varchar AS mejor_si
    FROM k1
    UNION ALL
    SELECT 2, 'KPI2', 'Demanda no atendida',
           CASE WHEN k2.den > 0 THEN round(k2.num * 100.0 / k2.den, 1) END, '%',
           k2.num, k2.den::integer,
           format('%s de %s unidades solicitadas', k2.num, k2.den), 'menor'
    FROM k2
    UNION ALL
    SELECT 3, 'KPI3', 'Baja rotación',
           CASE WHEN k3.den > 0 THEN round(k3.num * 100.0 / k3.den, 1) END, '%',
           k3.num, k3.den::integer,
           format('%s de %s; %s %s con datos insuficientes', k3.num, k3.den, k3.insuficientes,
                  CASE WHEN k3.insuficientes = 1 THEN 'referencia' ELSE 'referencias' END), 'menor'
    FROM k3
    UNION ALL
    SELECT 4, 'KPI4', 'Tiempo de confirmación del proveedor',
           CASE WHEN k4.con_respuesta > 0 THEN round(k4.horas / k4.con_respuesta, 1) END, 'horas',
           round(k4.horas, 1), k4.con_respuesta::integer,
           format('%s pedido(s) con respuesta; %s enviado(s) sin respuesta (no se promedian)',
                  k4.con_respuesta, k4.sin_respuesta), 'menor'
    FROM k4
    UNION ALL
    SELECT 5, 'KPI5', 'Confirmados con el primer proveedor',
           CASE WHEN k5.den > 0 THEN round(k5.num * 100.0 / k5.den, 1) END, '%',
           k5.num, k5.den::integer,
           format('%s de %s pedidos confirmados lo fueron con el primer proveedor', k5.num, k5.den), 'mayor'
    FROM k5
  )
  SELECT p_corte, (p_corte - 29), p_corte, f.codigo, f.nombre, f.valor, f.unidad, f.numerador,
         f.denominador, f.detalle, f.mejor_si, fn_origen_datos()
  FROM filas f
  ORDER BY f.orden;
$$;

-- =============================================================================
-- VISTAS (corte vigente: fn_corte()). Son las que lee Power BI vía CSV.
-- Las de exportación usan fechas en hora local de Bogotá sin zona y SI/NO en
-- lugar de verdadero/falso, para que Excel y Power BI las lean sin conversiones.
-- Flask no las usa: llama a las funciones fn_* con el corte explícito.
-- =============================================================================

-- Saldo actual (todo lo registrado hasta hoy)
CREATE VIEW vw_saldos AS
SELECT p.id AS producto_id, p.sku, s.saldo, s.ultimo_conteo_en
FROM productos p
JOIN fn_saldos('infinity') s ON s.producto_id = p.id;

-- Estado actual: saldo de hoy + rotación del periodo de corte
CREATE VIEW vw_estado_productos AS
SELECT p.id AS producto_id, p.sku, p.nombre, e.saldo, e.umbral_reposicion, e.estado,
       e.dias_con_registro, e.vendidas_30d, e.no_atendidas_30d, e.demanda_diaria, e.cobertura_dias,
       fn_corte() AS corte
FROM productos p
JOIN fn_estado_productos(fn_corte(), 'infinity') e ON e.producto_id = p.id;

CREATE VIEW vw_sugeridos AS
SELECT p.id AS producto_id, p.sku, p.nombre, s.saldo, s.demanda_diaria, s.cobertura_dias,
       pr.plazo_entrega_dias, s.sugerido, s.formula, s.regla_version,
       fn_corte() AS corte, fn_origen_datos() AS origen_datos
FROM productos p
JOIN proveedores pr ON pr.id = p.proveedor_id
JOIN fn_sugeridos(fn_corte(), fn_limite_corte(fn_corte()), 14) s ON s.producto_id = p.id
WHERE p.activo;

-- --- Exportación a CSV (Power BI) --------------------------------------------

-- Inventario y estado AL CORTE (para que cuadre con el KPI 1)
CREATE VIEW vw_inventario_actual AS
SELECT fn_corte() AS corte,
       p.id AS producto_id, p.sku, p.nombre, c.nombre AS categoria,
       pr.nombre AS proveedor, pr.plazo_entrega_dias,
       p.presentacion, p.unidad_medida, p.umbral_reposicion,
       e.saldo, e.estado, e.dias_con_registro,
       e.vendidas_30d, e.no_atendidas_30d, e.demanda_30d, e.demanda_diaria, e.cobertura_dias,
       CASE WHEN e.cobertura_dias IS NOT NULL AND e.cobertura_dias < pr.plazo_entrega_dias THEN 'SI' ELSE 'NO' END
         AS cobertura_menor_que_plazo,
       s.sugerido AS sugerido_14d,
       fn_origen_datos() AS origen_datos
FROM productos p
JOIN categorias c ON c.id = p.categoria_id
JOIN proveedores pr ON pr.id = p.proveedor_id
JOIN fn_estado_productos(fn_corte(), fn_limite_corte(fn_corte())) e ON e.producto_id = p.id
JOIN fn_sugeridos(fn_corte(), fn_limite_corte(fn_corte()), 14) s ON s.producto_id = p.id
WHERE p.activo
  AND p.creado_en < fn_limite_corte(fn_corte())   -- un producto creado después del corte no existía en el periodo
ORDER BY p.id;

-- Un renglón por día del periodo y por producto (incluye días sin movimiento)
CREATE VIEW vw_ventas_diarias AS
WITH dias AS (
  SELECT generate_series(fn_corte() - 29, fn_corte(), interval '1 day')::date AS fecha
),
ventas AS (
  SELECT m.producto_id, (m.fecha_hora AT TIME ZONE 'America/Bogota')::date AS fecha, sum(m.cantidad) AS vendidas
  FROM movimientos m
  WHERE m.tipo = 'VENTA'
    AND m.fecha_hora >= fn_limite_corte(fn_corte()) - interval '30 days'
    AND m.fecha_hora < fn_limite_corte(fn_corte())
  GROUP BY 1, 2
),
sol AS (
  SELECT s.producto_id, (s.fecha_hora AT TIME ZONE 'America/Bogota')::date AS fecha,
         sum(s.cantidad_solicitada) AS solicitadas,
         sum(s.cantidad_solicitada - s.cantidad_entregada) AS no_atendidas,
         count(*) AS atenciones
  FROM solicitudes_clientes s
  WHERE s.solicitud_previa_id IS NULL
    AND s.fecha_hora >= fn_limite_corte(fn_corte()) - interval '30 days'
    AND s.fecha_hora < fn_limite_corte(fn_corte())
  GROUP BY 1, 2
)
SELECT d.fecha, p.id AS producto_id, p.sku, p.nombre, c.nombre AS categoria,
       COALESCE(v.vendidas, 0)::integer AS vendidas,
       COALESCE(s.solicitadas, 0)::integer AS solicitadas,
       COALESCE(s.no_atendidas, 0)::integer AS no_atendidas,
       COALESCE(s.atenciones, 0)::integer AS atenciones,
       fn_corte() AS corte,
       fn_origen_datos() AS origen_datos
FROM dias d
CROSS JOIN productos p
JOIN categorias c ON c.id = p.categoria_id
LEFT JOIN ventas v ON v.producto_id = p.id AND v.fecha = d.fecha
LEFT JOIN sol s ON s.producto_id = p.id AND s.fecha = d.fecha
WHERE p.activo
  AND p.creado_en < fn_limite_corte(fn_corte())
ORDER BY d.fecha, p.id;

-- Cada atención al cliente del periodo (sin datos del cliente)
CREATE VIEW vw_solicitudes AS
SELECT s.id AS solicitud_id,
       (s.fecha_hora AT TIME ZONE 'America/Bogota')::timestamp(0) AS fecha_hora,
       (s.fecha_hora AT TIME ZONE 'America/Bogota')::date AS fecha,
       p.id AS producto_id, p.sku, p.nombre, c.nombre AS categoria,
       s.cantidad_solicitada,
       s.cantidad_entregada,
       s.cantidad_solicitada - s.cantidad_entregada AS no_atendida,
       CASE WHEN s.solicitud_previa_id IS NOT NULL THEN 'SI' ELSE 'NO' END AS es_regreso,
       s.solicitud_previa_id,
       CASE WHEN s.solicitud_previa_id IS NULL THEN 'SI' ELSE 'NO' END AS cuenta_en_kpi2,
       u.rol AS registrado_por_rol,
       fn_corte() AS corte,
       fn_origen_datos() AS origen_datos
FROM solicitudes_clientes s
JOIN productos p ON p.id = s.producto_id
JOIN categorias c ON c.id = p.categoria_id
JOIN usuarios u ON u.id = s.usuario_id
WHERE s.fecha_hora >= fn_limite_corte(fn_corte()) - interval '30 days'
  AND s.fecha_hora < fn_limite_corte(fn_corte())
ORDER BY s.fecha_hora, s.id;

-- Pedidos creados hasta el corte, con su cadena de reintentos
CREATE VIEW vw_pedidos AS
WITH RECURSIVE cadena AS (
  SELECT pe.id, pe.id AS cadena_id FROM pedidos pe WHERE pe.pedido_anterior_id IS NULL
  UNION ALL
  SELECT hijo.id, c.cadena_id FROM pedidos hijo JOIN cadena c ON hijo.pedido_anterior_id = c.id
),
det AS (
  SELECT d.pedido_id,
         count(*) AS referencias,
         sum(d.cantidad_solicitada) AS unidades_solicitadas,
         sum(d.cantidad_sugerida) AS unidades_sugeridas,
         string_agg(p.sku, ', ' ORDER BY p.sku) AS skus
  FROM pedido_detalles d JOIN productos p ON p.id = d.producto_id
  GROUP BY d.pedido_id
)
SELECT pe.id AS pedido_id,
       ca.cadena_id,
       pe.numero_intento,
       pe.pedido_anterior_id,
       pr.nombre AS proveedor,
       pr.plazo_entrega_dias,
       pe.estado,
       (pe.fecha_creacion   AT TIME ZONE 'America/Bogota')::timestamp(0) AS fecha_creacion,
       (pe.fecha_aprobacion AT TIME ZONE 'America/Bogota')::timestamp(0) AS fecha_aprobacion,
       (pe.fecha_envio      AT TIME ZONE 'America/Bogota')::timestamp(0) AS fecha_envio,
       (pe.fecha_respuesta  AT TIME ZONE 'America/Bogota')::timestamp(0) AS fecha_respuesta,
       pe.fecha_entrega_estimada,
       CASE WHEN pe.fecha_respuesta IS NOT NULL AND pe.fecha_envio IS NOT NULL
            THEN round(extract(epoch FROM (pe.fecha_respuesta - pe.fecha_envio)) / 3600.0, 1) END AS horas_respuesta,
       -- Enviado y sin respuesta: horas esperando hasta el corte
       CASE WHEN pe.estado = 'ENVIADO' AND pe.fecha_respuesta IS NULL
            THEN round(extract(epoch FROM (fn_limite_corte(fn_corte()) - pe.fecha_envio)) / 3600.0, 1) END AS horas_esperando_al_corte,
       CASE WHEN pe.estado = 'CONFIRMADO' AND pe.numero_intento = 1 THEN 'SI' ELSE 'NO' END AS confirmado_primer_proveedor,
       pe.motivo_cancelacion,
       COALESCE(det.referencias, 0)::integer AS referencias,
       COALESCE(det.unidades_solicitadas, 0)::integer AS unidades_solicitadas,
       det.unidades_sugeridas::integer AS unidades_sugeridas,
       det.skus,
       fn_corte() AS corte,
       fn_origen_datos() AS origen_datos
FROM pedidos pe
JOIN cadena ca ON ca.id = pe.id
JOIN proveedores pr ON pr.id = pe.proveedor_id
LEFT JOIN det ON det.pedido_id = pe.id
WHERE pe.fecha_creacion < fn_limite_corte(fn_corte())
ORDER BY pe.id;

-- KPI del corte vigente: una fila por KPI
CREATE VIEW vw_kpi_resumen AS
SELECT * FROM fn_kpi_resumen(fn_corte());

CREATE VIEW vw_kpi_agotadas          AS SELECT * FROM vw_kpi_resumen WHERE codigo = 'KPI1';
CREATE VIEW vw_kpi_demanda           AS SELECT * FROM vw_kpi_resumen WHERE codigo = 'KPI2';
CREATE VIEW vw_kpi_rotacion          AS SELECT * FROM vw_kpi_resumen WHERE codigo = 'KPI3';
CREATE VIEW vw_kpi_respuesta         AS SELECT * FROM vw_kpi_resumen WHERE codigo = 'KPI4';
CREATE VIEW vw_kpi_primer_proveedor  AS SELECT * FROM vw_kpi_resumen WHERE codigo = 'KPI5';

COMMENT ON VIEW vw_kpi_resumen IS 'Los 5 KPI del corte vigente. Fuente única para Flask y Power BI.';
COMMENT ON VIEW vw_inventario_actual IS 'Estado de cada referencia AL CORTE (no en vivo): cuadra con el KPI 1.';
