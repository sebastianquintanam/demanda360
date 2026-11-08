-- =============================================================================
-- Demanda360 · DATOS SIMULADOS de septiembre de 2026 (no son datos del negocio)
-- ARCHIVO GENERADO por database/seeds/generar_demo.py: no se edita a mano.
-- 89 atenciones · 127 unidades vendidas · 12 no atendidas · 5 pedidos
-- Requisitos: base con 01_schema.sql y 02_vistas.sql, SIN productos, y con los
-- usuarios 'propietario' y 'trabajador' (flask crear-usuarios-demo).
-- Cargar: flask cargar-demo  (o psql -v ON_ERROR_STOP=1 -f database/seeds/10_demo.sql)
-- =============================================================================

SET client_encoding = 'UTF8';
SET timezone = 'America/Bogota';
BEGIN;

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM productos) OR EXISTS (SELECT 1 FROM movimientos) THEN
    RAISE EXCEPTION 'La base ya tiene productos o movimientos: los datos demo solo se cargan en una base vacía.';
  END IF;
  IF (SELECT count(*) FROM usuarios WHERE usuario IN ('propietario', 'trabajador')) <> 2 THEN
    RAISE EXCEPTION 'Faltan los usuarios propietario y trabajador: corre primero flask crear-usuarios-demo.';
  END IF;
END
$$;

-- Ayudantes temporales (solo existen durante esta carga)
CREATE FUNCTION pg_temp.uid(p_usuario text) RETURNS bigint LANGUAGE sql STABLE AS
  $$ SELECT id FROM usuarios WHERE usuario = p_usuario $$;
CREATE FUNCTION pg_temp.pid(p_sku text) RETURNS bigint LANGUAGE sql STABLE AS
  $$ SELECT id FROM productos WHERE sku = p_sku $$;
CREATE FUNCTION pg_temp.atencion(p_ref text, p_sku text, p_solicitada int, p_entregada int,
                                 p_fecha timestamptz, p_usuario text) RETURNS void LANGUAGE plpgsql AS $$
DECLARE v_mov bigint;
BEGIN
  IF p_entregada > 0 THEN
    INSERT INTO movimientos (producto_id, tipo, cantidad, fecha_hora, usuario_id, origen_ref)
    VALUES (pg_temp.pid(p_sku), 'VENTA', p_entregada, p_fecha, pg_temp.uid(p_usuario), p_ref || '-VTA')
    RETURNING id INTO v_mov;
  END IF;
  INSERT INTO solicitudes_clientes (producto_id, cantidad_solicitada, cantidad_entregada, fecha_hora,
                                    usuario_id, movimiento_id, origen_ref)
  VALUES (pg_temp.pid(p_sku), p_solicitada, p_entregada, p_fecha, pg_temp.uid(p_usuario), v_mov, p_ref);
END $$;

-- Catálogo -------------------------------------------------------------------
INSERT INTO categorias (nombre) VALUES ('Lacas'), ('Esmaltes'), ('Selladores');
INSERT INTO proveedores (codigo, nombre, plazo_entrega_dias) VALUES
  ('SUM-AND', 'Suministros Andinos (ficticio)', 3),
  ('DIS-COR', 'Distribuidora Cordillera (ficticio)', 4),
  ('QUI-SAB', 'Químicos La Sabana (ficticio)', 5),
  ('PIN-LLA', 'Pinturas del Llano (ficticio)', 7);
INSERT INTO productos (sku, nombre, categoria_id, proveedor_id, marca, presentacion, unidad_medida,
                       costo_compra, precio_venta, umbral_reposicion, creado_en) VALUES
  ('LAC-BP-01', 'Laca catalizada alto brillo galón', (SELECT id FROM categorias WHERE nombre = 'Lacas'), (SELECT id FROM proveedores WHERE codigo = 'SUM-AND'), 'ColorNova (ficticia)', 'Galón', 'galon', 85000, 110000, 6, '2026-09-01 07:00:00-05'),
  ('LAC-BP-02', 'Laca catalizada mate galón', (SELECT id FROM categorias WHERE nombre = 'Lacas'), (SELECT id FROM proveedores WHERE codigo = 'DIS-COR'), 'ColorNova (ficticia)', 'Galón', 'galon', 82000, 106000, 4, '2026-09-01 07:00:00-05'),
  ('ESM-WH-01', 'Esmalte blanco galón', (SELECT id FROM categorias WHERE nombre = 'Esmaltes'), (SELECT id FROM proveedores WHERE codigo = 'SUM-AND'), 'ColorNova (ficticia)', 'Galón', 'galon', 52000, 68000, 4, '2026-09-01 07:00:00-05'),
  ('SEL-AQ-01', 'Sellador acuático galón', (SELECT id FROM categorias WHERE nombre = 'Selladores'), (SELECT id FROM proveedores WHERE codigo = 'QUI-SAB'), 'ColorNova (ficticia)', 'Galón', 'galon', 47000, 62000, 6, '2026-09-01 07:00:00-05'),
  ('SEL-CA-01', 'Sellador catalizado 45 % galón', (SELECT id FROM categorias WHERE nombre = 'Selladores'), (SELECT id FROM proveedores WHERE codigo = 'QUI-SAB'), 'ColorNova (ficticia)', 'Galón', 'galon', 58000, 76000, 4, '2026-09-01 07:00:00-05'),
  ('LAC-TR-01', 'Laca transparente galón', (SELECT id FROM categorias WHERE nombre = 'Lacas'), (SELECT id FROM proveedores WHERE codigo = 'DIS-COR'), 'ColorNova (ficticia)', 'Galón', 'galon', 80000, 104000, 3, '2026-09-28 09:30:00-05'),
  ('ESM-SI-01', 'Esmalte sintético cuñete', (SELECT id FROM categorias WHERE nombre = 'Esmaltes'), (SELECT id FROM proveedores WHERE codigo = 'PIN-LLA'), 'ColorNova (ficticia)', 'Cuñete', 'cunete', 210000, 265000, 2, '2026-09-01 07:00:00-05'),
  ('SEL-AC-01', 'Sellador acrílico galón', (SELECT id FROM categorias WHERE nombre = 'Selladores'), (SELECT id FROM proveedores WHERE codigo = 'QUI-SAB'), 'ColorNova (ficticia)', 'Galón', 'galon', 45000, 59000, 3, '2026-09-01 07:00:00-05'),
  ('LAC-NG-01', 'Laca nogal galón', (SELECT id FROM categorias WHERE nombre = 'Lacas'), (SELECT id FROM proveedores WHERE codigo = 'DIS-COR'), 'ColorNova (ficticia)', 'Galón', 'galon', 78000, 101000, 3, '2026-09-01 07:00:00-05'),
  ('ESM-RJ-01', 'Esmalte rojo galón', (SELECT id FROM categorias WHERE nombre = 'Esmaltes'), (SELECT id FROM proveedores WHERE codigo = 'SUM-AND'), 'ColorNova (ficticia)', 'Galón', 'galon', 54000, 70000, 3, '2026-09-01 07:00:00-05'),
  ('SEL-MU-01', 'Sellador para muros cuñete', (SELECT id FROM categorias WHERE nombre = 'Selladores'), (SELECT id FROM proveedores WHERE codigo = 'QUI-SAB'), 'ColorNova (ficticia)', 'Cuñete', 'cunete', 190000, 240000, 3, '2026-09-01 07:00:00-05');

-- Conteos iniciales (la existencia inicial es un conteo) ----------------------
INSERT INTO conteos_fisicos (producto_id, cantidad_contada, fecha_hora, usuario_id, observaciones, origen_ref) VALUES
  (pg_temp.pid('LAC-BP-01'), 20, '2026-09-01 07:30:00-05', pg_temp.uid('propietario'), 'Conteo inicial', 'DEMO-CNT-INI-LAC-BP-01'),
  (pg_temp.pid('LAC-BP-02'), 8, '2026-09-01 07:30:00-05', pg_temp.uid('propietario'), 'Conteo inicial', 'DEMO-CNT-INI-LAC-BP-02'),
  (pg_temp.pid('ESM-WH-01'), 24, '2026-09-01 07:30:00-05', pg_temp.uid('propietario'), 'Conteo inicial', 'DEMO-CNT-INI-ESM-WH-01'),
  (pg_temp.pid('SEL-AQ-01'), 12, '2026-09-01 07:30:00-05', pg_temp.uid('propietario'), 'Conteo inicial', 'DEMO-CNT-INI-SEL-AQ-01'),
  (pg_temp.pid('SEL-CA-01'), 16, '2026-09-01 07:30:00-05', pg_temp.uid('propietario'), 'Conteo inicial', 'DEMO-CNT-INI-SEL-CA-01'),
  (pg_temp.pid('LAC-TR-01'), 10, '2026-09-28 10:00:00-05', pg_temp.uid('propietario'), 'Conteo inicial: referencia nueva en el catálogo', 'DEMO-CNT-INI-LAC-TR-01'),
  (pg_temp.pid('ESM-SI-01'), 17, '2026-09-01 07:30:00-05', pg_temp.uid('propietario'), 'Conteo inicial', 'DEMO-CNT-INI-ESM-SI-01'),
  (pg_temp.pid('SEL-AC-01'), 13, '2026-09-01 07:30:00-05', pg_temp.uid('propietario'), 'Conteo inicial', 'DEMO-CNT-INI-SEL-AC-01'),
  (pg_temp.pid('LAC-NG-01'), 10, '2026-09-01 07:30:00-05', pg_temp.uid('propietario'), 'Conteo inicial', 'DEMO-CNT-INI-LAC-NG-01'),
  (pg_temp.pid('ESM-RJ-01'), 11, '2026-09-01 07:30:00-05', pg_temp.uid('propietario'), 'Conteo inicial', 'DEMO-CNT-INI-ESM-RJ-01'),
  (pg_temp.pid('SEL-MU-01'), 13, '2026-09-01 07:30:00-05', pg_temp.uid('propietario'), 'Conteo inicial', 'DEMO-CNT-INI-SEL-MU-01');

-- Pedidos (P1) y sus detalles ---------------------------------------------------
INSERT INTO pedidos (proveedor_id, estado, numero_intento, pedido_anterior_id, creado_por, aprobado_por,
                     fecha_creacion, fecha_aprobacion, fecha_envio, fecha_respuesta, fecha_entrega_estimada, motivo_cancelacion)
VALUES ((SELECT id FROM proveedores WHERE codigo = 'SUM-AND'), 'CONFIRMADO', 1, NULL,
        pg_temp.uid('trabajador'), pg_temp.uid('propietario'), '2026-09-04 09:00:00-05', '2026-09-04 09:15:00-05',
        '2026-09-04 09:30:00-05', '2026-09-04 12:30:00-05', '2026-09-07', NULL);
INSERT INTO pedido_detalles (pedido_id, producto_id, cantidad_sugerida, cantidad_solicitada)
VALUES ((SELECT id FROM pedidos WHERE fecha_creacion = '2026-09-04 09:00:00-05'), pg_temp.pid('LAC-BP-01'), 25, 25);
INSERT INTO pedidos (proveedor_id, estado, numero_intento, pedido_anterior_id, creado_por, aprobado_por,
                     fecha_creacion, fecha_aprobacion, fecha_envio, fecha_respuesta, fecha_entrega_estimada, motivo_cancelacion)
VALUES ((SELECT id FROM proveedores WHERE codigo = 'DIS-COR'), 'CANCELADO', 1, NULL,
        pg_temp.uid('trabajador'), pg_temp.uid('propietario'), '2026-09-09 10:00:00-05', '2026-09-09 10:10:00-05',
        '2026-09-09 10:20:00-05', NULL, NULL, 'Sin respuesta del proveedor en 48 horas; se pide a otro proveedor');
INSERT INTO pedido_detalles (pedido_id, producto_id, cantidad_sugerida, cantidad_solicitada)
VALUES ((SELECT id FROM pedidos WHERE fecha_creacion = '2026-09-09 10:00:00-05'), pg_temp.pid('LAC-BP-02'), 10, 10);
INSERT INTO pedidos (proveedor_id, estado, numero_intento, pedido_anterior_id, creado_por, aprobado_por,
                     fecha_creacion, fecha_aprobacion, fecha_envio, fecha_respuesta, fecha_entrega_estimada, motivo_cancelacion)
VALUES ((SELECT id FROM proveedores WHERE codigo = 'SUM-AND'), 'CONFIRMADO', 2, (SELECT id FROM pedidos WHERE fecha_creacion = '2026-09-09 10:00:00-05'),
        pg_temp.uid('trabajador'), pg_temp.uid('propietario'), '2026-09-11 10:30:00-05', '2026-09-11 10:40:00-05',
        '2026-09-11 10:45:00-05', '2026-09-11 16:45:00-05', '2026-09-14', NULL);
INSERT INTO pedido_detalles (pedido_id, producto_id, cantidad_sugerida, cantidad_solicitada)
VALUES ((SELECT id FROM pedidos WHERE fecha_creacion = '2026-09-11 10:30:00-05'), pg_temp.pid('LAC-BP-02'), 10, 10);
INSERT INTO pedidos (proveedor_id, estado, numero_intento, pedido_anterior_id, creado_por, aprobado_por,
                     fecha_creacion, fecha_aprobacion, fecha_envio, fecha_respuesta, fecha_entrega_estimada, motivo_cancelacion)
VALUES ((SELECT id FROM proveedores WHERE codigo = 'QUI-SAB'), 'CONFIRMADO', 1, NULL,
        pg_temp.uid('trabajador'), pg_temp.uid('propietario'), '2026-09-14 09:00:00-05', '2026-09-14 09:20:00-05',
        '2026-09-14 09:30:00-05', '2026-09-14 14:30:00-05', '2026-09-19', NULL);
INSERT INTO pedido_detalles (pedido_id, producto_id, cantidad_sugerida, cantidad_solicitada)
VALUES ((SELECT id FROM pedidos WHERE fecha_creacion = '2026-09-14 09:00:00-05'), pg_temp.pid('SEL-AQ-01'), 13, 13);
INSERT INTO pedidos (proveedor_id, estado, numero_intento, pedido_anterior_id, creado_por, aprobado_por,
                     fecha_creacion, fecha_aprobacion, fecha_envio, fecha_respuesta, fecha_entrega_estimada, motivo_cancelacion)
VALUES ((SELECT id FROM proveedores WHERE codigo = 'SUM-AND'), 'ENVIADO', 1, NULL,
        pg_temp.uid('trabajador'), pg_temp.uid('propietario'), '2026-09-28 09:00:00-05', '2026-09-28 09:10:00-05',
        '2026-09-28 09:20:00-05', NULL, NULL, NULL);
INSERT INTO pedido_detalles (pedido_id, producto_id, cantidad_sugerida, cantidad_solicitada)
VALUES ((SELECT id FROM pedidos WHERE fecha_creacion = '2026-09-28 09:00:00-05'), pg_temp.pid('ESM-WH-01'), 13, 13);

-- Entradas de mercancía y ajustes -------------------------------------------
INSERT INTO movimientos (producto_id, tipo, cantidad, fecha_hora, usuario_id, origen_ref, justificacion) VALUES (pg_temp.pid('LAC-BP-01'), 'ENTRADA', 25, '2026-09-07 08:15:00-05', pg_temp.uid('propietario'), 'DEMO-ENT-0907-LAC-BP-01', NULL);
INSERT INTO movimientos (producto_id, tipo, cantidad, fecha_hora, usuario_id, origen_ref, justificacion) VALUES (pg_temp.pid('LAC-BP-02'), 'ENTRADA', 10, '2026-09-14 08:15:00-05', pg_temp.uid('propietario'), 'DEMO-ENT-0914-LAC-BP-02', NULL);
INSERT INTO movimientos (producto_id, tipo, cantidad, fecha_hora, usuario_id, origen_ref, justificacion) VALUES (pg_temp.pid('SEL-AQ-01'), 'ENTRADA', 13, '2026-09-19 08:15:00-05', pg_temp.uid('propietario'), 'DEMO-ENT-0919-SEL-AQ-01', NULL);
INSERT INTO movimientos (producto_id, tipo, cantidad, fecha_hora, usuario_id, origen_ref, justificacion) VALUES (pg_temp.pid('ESM-RJ-01'), 'AJUSTE', -1, '2026-09-21 09:40:00-05', pg_temp.uid('propietario'), 'DEMO-AJU-0921-ESM-RJ-01', 'Galón con la tapa rota en bodega; se retira de la venta');

-- Atenciones a clientes (89): solicitado, entregado y la venta si hubo entrega
DO $do$
BEGIN
  PERFORM pg_temp.atencion('DEMO-ATN-0001', 'SEL-AC-01', 1, 1, '2026-09-01 10:07:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0002', 'SEL-AQ-01', 1, 1, '2026-09-02 08:07:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0003', 'LAC-BP-01', 3, 3, '2026-09-02 13:01:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0004', 'LAC-BP-01', 3, 3, '2026-09-02 13:22:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0005', 'ESM-WH-01', 2, 2, '2026-09-02 13:43:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0006', 'LAC-BP-01', 2, 2, '2026-09-02 14:09:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0007', 'LAC-BP-01', 1, 1, '2026-09-02 16:16:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0008', 'LAC-BP-01', 1, 1, '2026-09-03 09:54:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0009', 'ESM-WH-01', 2, 2, '2026-09-03 12:05:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0010', 'LAC-BP-01', 2, 2, '2026-09-03 12:19:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0011', 'SEL-AQ-01', 2, 2, '2026-09-03 13:01:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0012', 'LAC-BP-01', 2, 2, '2026-09-03 14:16:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0013', 'SEL-CA-01', 2, 2, '2026-09-03 17:30:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0014', 'LAC-BP-02', 1, 1, '2026-09-05 09:07:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0015', 'SEL-AQ-01', 2, 2, '2026-09-05 14:21:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0016', 'LAC-BP-02', 2, 2, '2026-09-05 15:47:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0017', 'LAC-BP-01', 1, 1, '2026-09-05 17:01:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0018', 'ESM-WH-01', 1, 1, '2026-09-07 13:23:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0019', 'LAC-BP-01', 1, 1, '2026-09-07 17:20:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0020', 'SEL-AQ-01', 2, 2, '2026-09-08 08:30:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0021', 'LAC-BP-01', 1, 1, '2026-09-08 10:04:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0022', 'LAC-BP-01', 2, 2, '2026-09-08 11:10:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0023', 'LAC-BP-01', 1, 1, '2026-09-08 11:48:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0024', 'ESM-WH-01', 1, 1, '2026-09-08 11:55:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0025', 'SEL-CA-01', 2, 2, '2026-09-08 12:30:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0026', 'ESM-WH-01', 2, 2, '2026-09-08 16:25:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0027', 'ESM-SI-01', 1, 1, '2026-09-09 11:34:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0028', 'LAC-BP-02', 2, 2, '2026-09-09 13:47:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0029', 'ESM-WH-01', 1, 1, '2026-09-09 17:14:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0030', 'ESM-WH-01', 1, 1, '2026-09-10 09:05:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0031', 'LAC-BP-02', 2, 2, '2026-09-10 12:21:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0032', 'LAC-BP-02', 1, 1, '2026-09-10 15:14:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0033', 'SEL-AQ-01', 1, 1, '2026-09-10 16:33:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0034', 'SEL-AQ-01', 1, 1, '2026-09-11 09:43:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0035', 'SEL-MU-01', 1, 1, '2026-09-11 11:49:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0036', 'LAC-NG-01', 1, 1, '2026-09-11 16:38:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0037', 'LAC-BP-01', 1, 1, '2026-09-11 16:41:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0038', 'ESM-WH-01', 1, 1, '2026-09-12 11:03:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0039', 'ESM-WH-01', 1, 1, '2026-09-12 11:56:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0040', 'LAC-BP-01', 3, 3, '2026-09-12 12:30:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0041', 'LAC-BP-01', 1, 1, '2026-09-12 13:49:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0042', 'LAC-BP-01', 1, 1, '2026-09-12 16:04:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0043', 'SEL-CA-01', 1, 1, '2026-09-12 17:42:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0044', 'LAC-BP-02', 2, 2, '2026-09-14 08:16:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0045', 'LAC-BP-01', 2, 2, '2026-09-14 09:27:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0046', 'ESM-WH-01', 2, 2, '2026-09-15 08:00:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0047', 'SEL-AQ-01', 2, 2, '2026-09-15 10:25:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0048', 'SEL-CA-01', 1, 1, '2026-09-15 15:29:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0049', 'LAC-BP-01', 3, 3, '2026-09-15 17:43:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0050', 'ESM-SI-01', 1, 1, '2026-09-16 15:27:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0051', 'ESM-WH-01', 2, 2, '2026-09-17 11:23:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0052', 'SEL-AQ-01', 2, 1, '2026-09-18 10:13:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0053', 'ESM-WH-01', 1, 1, '2026-09-18 12:16:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0054', 'LAC-BP-01', 2, 2, '2026-09-18 17:15:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0055', 'LAC-BP-02', 2, 2, '2026-09-19 08:14:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0056', 'ESM-WH-01', 1, 1, '2026-09-19 08:47:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0057', 'LAC-BP-01', 3, 3, '2026-09-19 12:40:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0058', 'SEL-CA-01', 2, 2, '2026-09-19 15:39:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0059', 'LAC-BP-02', 1, 1, '2026-09-21 08:41:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0060', 'LAC-BP-01', 2, 2, '2026-09-21 09:22:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0061', 'LAC-BP-01', 2, 2, '2026-09-21 13:14:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0062', 'SEL-AQ-01', 1, 1, '2026-09-21 14:04:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0063', 'SEL-MU-01', 1, 1, '2026-09-21 15:16:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0064', 'LAC-BP-01', 3, 3, '2026-09-22 10:15:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0065', 'LAC-BP-01', 1, 1, '2026-09-22 13:19:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0066', 'ESM-WH-01', 1, 1, '2026-09-23 09:41:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0067', 'LAC-BP-02', 1, 1, '2026-09-23 13:17:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0068', 'ESM-WH-01', 2, 2, '2026-09-23 16:15:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0069', 'SEL-AQ-01', 2, 2, '2026-09-24 08:14:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0070', 'SEL-AQ-01', 2, 2, '2026-09-24 08:36:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0071', 'LAC-BP-01', 3, 1, '2026-09-24 11:18:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0072', 'ESM-WH-01', 2, 2, '2026-09-24 14:03:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0073', 'SEL-AQ-01', 2, 2, '2026-09-24 17:51:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0074', 'SEL-CA-01', 1, 1, '2026-09-25 08:12:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0075', 'SEL-CA-01', 2, 2, '2026-09-25 10:19:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0076', 'LAC-BP-02', 1, 1, '2026-09-25 15:11:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0077', 'LAC-BP-01', 2, 0, '2026-09-26 11:52:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0078', 'ESM-WH-01', 1, 1, '2026-09-26 12:37:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0079', 'LAC-BP-02', 1, 1, '2026-09-26 14:43:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0080', 'LAC-BP-02', 1, 1, '2026-09-28 09:24:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0081', 'SEL-AQ-01', 1, 1, '2026-09-28 11:23:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0082', 'LAC-BP-01', 2, 0, '2026-09-28 12:47:00-05', 'propietario');
  PERFORM pg_temp.atencion('DEMO-ATN-0083', 'SEL-CA-01', 1, 1, '2026-09-28 13:12:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0084', 'LAC-BP-02', 2, 1, '2026-09-28 13:49:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0085', 'ESM-WH-01', 1, 0, '2026-09-28 17:58:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0086', 'LAC-BP-02', 2, 0, '2026-09-30 08:41:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0087', 'LAC-TR-01', 1, 1, '2026-09-30 12:17:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0088', 'ESM-WH-01', 1, 0, '2026-09-30 13:00:00-05', 'trabajador');
  PERFORM pg_temp.atencion('DEMO-ATN-0089', 'LAC-TR-01', 1, 1, '2026-09-30 16:09:00-05', 'trabajador');
END
$do$;

-- Conteo de cierre del 30 de septiembre (coincide con el saldo calculado) ------
INSERT INTO conteos_fisicos (producto_id, cantidad_contada, fecha_hora, usuario_id, observaciones, origen_ref) VALUES
  (pg_temp.pid('LAC-BP-01'), 0, '2026-09-30 19:00:00-05', pg_temp.uid('propietario'), 'Conteo de cierre de mes', 'DEMO-CNT-FIN-LAC-BP-01'),
  (pg_temp.pid('LAC-BP-02'), 0, '2026-09-30 19:00:00-05', pg_temp.uid('propietario'), 'Conteo de cierre de mes', 'DEMO-CNT-FIN-LAC-BP-02'),
  (pg_temp.pid('ESM-WH-01'), 0, '2026-09-30 19:00:00-05', pg_temp.uid('propietario'), 'Conteo de cierre de mes', 'DEMO-CNT-FIN-ESM-WH-01'),
  (pg_temp.pid('SEL-AQ-01'), 5, '2026-09-30 19:00:00-05', pg_temp.uid('propietario'), 'Conteo de cierre de mes', 'DEMO-CNT-FIN-SEL-AQ-01'),
  (pg_temp.pid('SEL-CA-01'), 4, '2026-09-30 19:00:00-05', pg_temp.uid('propietario'), 'Conteo de cierre de mes', 'DEMO-CNT-FIN-SEL-CA-01'),
  (pg_temp.pid('LAC-TR-01'), 8, '2026-09-30 19:00:00-05', pg_temp.uid('propietario'), 'Conteo de cierre de mes', 'DEMO-CNT-FIN-LAC-TR-01'),
  (pg_temp.pid('ESM-SI-01'), 15, '2026-09-30 19:00:00-05', pg_temp.uid('propietario'), 'Conteo de cierre de mes', 'DEMO-CNT-FIN-ESM-SI-01'),
  (pg_temp.pid('SEL-AC-01'), 12, '2026-09-30 19:00:00-05', pg_temp.uid('propietario'), 'Conteo de cierre de mes', 'DEMO-CNT-FIN-SEL-AC-01'),
  (pg_temp.pid('LAC-NG-01'), 9, '2026-09-30 19:00:00-05', pg_temp.uid('propietario'), 'Conteo de cierre de mes', 'DEMO-CNT-FIN-LAC-NG-01'),
  (pg_temp.pid('ESM-RJ-01'), 10, '2026-09-30 19:00:00-05', pg_temp.uid('propietario'), 'Conteo de cierre de mes', 'DEMO-CNT-FIN-ESM-RJ-01'),
  (pg_temp.pid('SEL-MU-01'), 11, '2026-09-30 19:00:00-05', pg_temp.uid('propietario'), 'Conteo de cierre de mes', 'DEMO-CNT-FIN-SEL-MU-01');

-- Bitácora de la carga -----------------------------------------------------------
INSERT INTO auditoria (usuario_id, accion, entidad, entidad_id, detalle) VALUES
  (NULL, 'DATOS_DEMO_CARGADOS', 'sistema', NULL, '{"origen_datos": "SIMULADO", "periodo": "2026-09", "referencias": 11, "atenciones": 89, "pedidos": 5}'::jsonb);

-- Verificación: si algo no cuadra con el Figma, la carga completa se deshace
DO $$
DECLARE v record;
BEGIN
  FOR v IN SELECT codigo, valor FROM fn_kpi_resumen(DATE '2026-09-30') WHERE codigo IN ('KPI1', 'KPI2', 'KPI3') LOOP
    IF (v.codigo, v.valor) NOT IN (('KPI1', 27.3), ('KPI2', 8.6), ('KPI3', 50.0)) THEN
      RAISE EXCEPTION 'El % dio % y no la cifra del Figma', v.codigo, v.valor;
    END IF;
  END LOOP;
END
$$;

COMMIT;
