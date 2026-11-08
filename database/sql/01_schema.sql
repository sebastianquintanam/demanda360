-- =============================================================================
-- Demanda360 · Esquema de la base de datos (fuente de verdad)
-- PostgreSQL 16 · Lo carga el contenedor `db` la primera vez que arranca
-- (docker-entrypoint-initdb.d). SQLAlchemy solo mapea estas tablas: no hay
-- create_all ni migraciones. Cualquier cambio aquí entra por pull request.
--
-- Reglas que el esquema protege por sí mismo (aunque falle el backend):
--   * El saldo NO se guarda en ninguna tabla: se calcula (ver 02_vistas.sql).
--   * SKU único y normalizado en mayúsculas.
--   * Cantidades enteras con CHECK; ajustes ≠ 0 y con justificación.
--   * Movimientos, conteos, solicitudes y auditoría no se modifican ni se
--     borran (trigger). Una corrección es un AJUSTE nuevo o un conteo nuevo.
--   * origen_ref único para que un formulario reenviado no duplique registros.
-- =============================================================================

SET client_encoding = 'UTF8';

-- Zona horaria de la base: Bogotá. Todas las fechas son timestamptz.
DO $$
BEGIN
  EXECUTE format('ALTER DATABASE %I SET timezone TO %L', current_database(), 'America/Bogota');
END
$$;
SET timezone = 'America/Bogota';

-- -----------------------------------------------------------------------------
-- Función común: bloquea UPDATE y DELETE en tablas de solo inserción
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_bloquear_modificacion()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  RAISE EXCEPTION 'La tabla % es de solo inserción: % no está permitido. Registre un ajuste o un conteo nuevo.',
    TG_TABLE_NAME, TG_OP
    USING ERRCODE = 'restrict_violation';
END;
$$;

-- -----------------------------------------------------------------------------
-- usuarios (P0)
-- -----------------------------------------------------------------------------
CREATE TABLE usuarios (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nombre         varchar(120) NOT NULL,
  usuario        varchar(50)  NOT NULL,
  password_hash  varchar(255) NOT NULL,
  rol            varchar(20)  NOT NULL,
  activo         boolean      NOT NULL DEFAULT true,
  creado_en      timestamptz  NOT NULL DEFAULT now(),
  CONSTRAINT uq_usuarios_usuario UNIQUE (usuario),
  CONSTRAINT ck_usuarios_usuario_minusculas CHECK (usuario = lower(usuario) AND length(usuario) >= 3),
  CONSTRAINT ck_usuarios_rol CHECK (rol IN ('propietario', 'trabajador'))
);
COMMENT ON TABLE usuarios IS 'Personas que usan el sistema. Solo se guarda el hash de la contraseña.';

-- -----------------------------------------------------------------------------
-- categorias (P0)
-- -----------------------------------------------------------------------------
CREATE TABLE categorias (
  id      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nombre  varchar(80) NOT NULL,
  CONSTRAINT ck_categorias_nombre CHECK (length(btrim(nombre)) > 0)
);
-- "Laca" y "laca" no pueden ser dos categorías distintas
CREATE UNIQUE INDEX uq_categorias_nombre_ci ON categorias (lower(btrim(nombre)));

-- -----------------------------------------------------------------------------
-- proveedores (P0) · contacto opcional (minimización de datos, Ley 1581/2012)
-- -----------------------------------------------------------------------------
CREATE TABLE proveedores (
  id                  bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  codigo              varchar(20)  NOT NULL,
  nombre              varchar(120) NOT NULL,
  plazo_entrega_dias  integer      NOT NULL,
  contacto            varchar(120),
  activo              boolean      NOT NULL DEFAULT true,
  creado_en           timestamptz  NOT NULL DEFAULT now(),
  CONSTRAINT uq_proveedores_codigo UNIQUE (codigo),
  CONSTRAINT ck_proveedores_codigo CHECK (codigo = upper(codigo)),
  CONSTRAINT ck_proveedores_plazo CHECK (plazo_entrega_dias > 0)
);
COMMENT ON COLUMN proveedores.plazo_entrega_dias IS 'Días de entrega (2 a 5 según el negocio). NO es el tiempo de respuesta del proveedor.';

-- -----------------------------------------------------------------------------
-- productos (P0) · sin columna de saldo a propósito
-- -----------------------------------------------------------------------------
CREATE TABLE productos (
  id                 bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  sku                varchar(30)   NOT NULL,
  nombre             varchar(150)  NOT NULL,
  categoria_id       bigint        NOT NULL REFERENCES categorias (id),
  proveedor_id       bigint        NOT NULL REFERENCES proveedores (id),
  marca              varchar(80),
  presentacion       varchar(60)   NOT NULL,
  unidad_medida      varchar(20)   NOT NULL,
  costo_compra       numeric(12,2) NOT NULL,
  precio_venta       numeric(12,2) NOT NULL,
  umbral_reposicion  integer       NOT NULL,
  activo             boolean       NOT NULL DEFAULT true,
  creado_en          timestamptz   NOT NULL DEFAULT now(),
  CONSTRAINT uq_productos_sku UNIQUE (sku),
  CONSTRAINT ck_productos_sku_formato CHECK (sku ~ '^[A-Z0-9][A-Z0-9-]{2,29}$'),
  CONSTRAINT ck_productos_nombre CHECK (length(btrim(nombre)) > 0),
  CONSTRAINT ck_productos_unidad CHECK (unidad_medida IN
    ('unidad', 'galon', 'medio_galon', 'cuarto_galon', 'cunete', 'litro', 'kilogramo')),
  CONSTRAINT ck_productos_costo CHECK (costo_compra >= 0),
  CONSTRAINT ck_productos_precio CHECK (precio_venta >= 0),
  CONSTRAINT ck_productos_umbral CHECK (umbral_reposicion >= 0)
);
CREATE INDEX ix_productos_categoria ON productos (categoria_id);
CREATE INDEX ix_productos_proveedor ON productos (proveedor_id);
COMMENT ON TABLE productos IS 'Catálogo. El SKU distingue presentaciones (galón ≠ medio galón). El saldo se calcula, nunca se guarda.';
COMMENT ON COLUMN productos.umbral_reposicion IS 'Lo define el propietario. Saldo ≤ umbral = Crítico.';

-- -----------------------------------------------------------------------------
-- conteos_fisicos (P0) · la existencia inicial también es un conteo
-- -----------------------------------------------------------------------------
CREATE TABLE conteos_fisicos (
  id                bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  producto_id       bigint       NOT NULL REFERENCES productos (id),
  cantidad_contada  integer      NOT NULL,
  fecha_hora        timestamptz  NOT NULL DEFAULT now(),
  usuario_id        bigint       NOT NULL REFERENCES usuarios (id),
  observaciones     varchar(300),
  origen_ref        varchar(64),
  CONSTRAINT ck_conteos_cantidad CHECK (cantidad_contada >= 0),
  CONSTRAINT uq_conteos_origen_ref UNIQUE (origen_ref)
);
CREATE INDEX ix_conteos_producto_fecha ON conteos_fisicos (producto_id, fecha_hora DESC);
CREATE INDEX ix_conteos_usuario ON conteos_fisicos (usuario_id);
CREATE TRIGGER tg_conteos_solo_insercion
  BEFORE UPDATE OR DELETE ON conteos_fisicos
  FOR EACH ROW EXECUTE FUNCTION fn_bloquear_modificacion();

-- -----------------------------------------------------------------------------
-- movimientos (P0) · VENTA, ENTRADA, AJUSTE · nunca se borran
-- origen_ref es texto (no uuid) para admitir folios manuales de contingencia.
-- -----------------------------------------------------------------------------
CREATE TABLE movimientos (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  producto_id    bigint       NOT NULL REFERENCES productos (id),
  tipo           varchar(10)  NOT NULL,
  cantidad       integer      NOT NULL,
  fecha_hora     timestamptz  NOT NULL DEFAULT now(),
  usuario_id     bigint       NOT NULL REFERENCES usuarios (id),
  origen_ref     varchar(64)  NOT NULL,
  justificacion  varchar(500),
  CONSTRAINT uq_movimientos_origen_ref UNIQUE (origen_ref),
  CONSTRAINT ck_movimientos_tipo CHECK (tipo IN ('VENTA', 'ENTRADA', 'AJUSTE')),
  CONSTRAINT ck_movimientos_cantidad CHECK (
       (tipo IN ('VENTA', 'ENTRADA') AND cantidad > 0)
    OR (tipo = 'AJUSTE' AND cantidad <> 0)
  ),
  CONSTRAINT ck_movimientos_ajuste_justificado CHECK (
    tipo <> 'AJUSTE' OR (justificacion IS NOT NULL AND length(btrim(justificacion)) >= 10)
  )
);
CREATE INDEX ix_movimientos_producto_fecha ON movimientos (producto_id, fecha_hora);
CREATE INDEX ix_movimientos_usuario ON movimientos (usuario_id);
CREATE TRIGGER tg_movimientos_solo_insercion
  BEFORE UPDATE OR DELETE ON movimientos
  FOR EACH ROW EXECUTE FUNCTION fn_bloquear_modificacion();
COMMENT ON COLUMN movimientos.cantidad IS 'VENTA y ENTRADA > 0 (el signo lo da el tipo). AJUSTE con signo: +n suma, -n resta.';

-- -----------------------------------------------------------------------------
-- solicitudes_clientes (P0) · una fila por atención: lo que pidió y lo entregado
-- Sin datos del cliente. La demanda no atendida = solicitada - entregada.
-- -----------------------------------------------------------------------------
CREATE TABLE solicitudes_clientes (
  id                   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  producto_id          bigint       NOT NULL REFERENCES productos (id),
  cantidad_solicitada  integer      NOT NULL,
  cantidad_entregada   integer      NOT NULL,
  fecha_hora           timestamptz  NOT NULL DEFAULT now(),
  usuario_id           bigint       NOT NULL REFERENCES usuarios (id),
  movimiento_id        bigint       REFERENCES movimientos (id),
  solicitud_previa_id  bigint       REFERENCES solicitudes_clientes (id),
  origen_ref           varchar(64)  NOT NULL,
  CONSTRAINT uq_solicitudes_origen_ref UNIQUE (origen_ref),
  CONSTRAINT uq_solicitudes_movimiento UNIQUE (movimiento_id),
  CONSTRAINT ck_solicitudes_solicitada CHECK (cantidad_solicitada > 0),
  CONSTRAINT ck_solicitudes_entregada CHECK (cantidad_entregada >= 0 AND cantidad_entregada <= cantidad_solicitada),
  -- Si se entregó algo, existe la VENTA; si no se entregó nada, no hay venta
  CONSTRAINT ck_solicitudes_venta CHECK ((cantidad_entregada > 0) = (movimiento_id IS NOT NULL)),
  CONSTRAINT ck_solicitudes_previa CHECK (solicitud_previa_id IS NULL OR solicitud_previa_id <> id)
);
CREATE INDEX ix_solicitudes_producto_fecha ON solicitudes_clientes (producto_id, fecha_hora);
CREATE INDEX ix_solicitudes_usuario ON solicitudes_clientes (usuario_id);
CREATE INDEX ix_solicitudes_previa ON solicitudes_clientes (solicitud_previa_id);
CREATE TRIGGER tg_solicitudes_solo_insercion
  BEFORE UPDATE OR DELETE ON solicitudes_clientes
  FOR EACH ROW EXECUTE FUNCTION fn_bloquear_modificacion();
COMMENT ON COLUMN solicitudes_clientes.solicitud_previa_id IS 'Cliente que regresa por lo que faltaba: esta atención NO suma demanda en el KPI 2.';

-- -----------------------------------------------------------------------------
-- auditoria (P0) · solo inserción; detalle mínimo en JSON, nunca contraseñas
-- -----------------------------------------------------------------------------
CREATE TABLE auditoria (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  usuario_id  bigint       REFERENCES usuarios (id),
  accion      varchar(50)  NOT NULL,
  entidad     varchar(50)  NOT NULL,
  entidad_id  bigint,
  fecha_hora  timestamptz  NOT NULL DEFAULT now(),
  detalle     jsonb        NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX ix_auditoria_fecha ON auditoria (fecha_hora DESC);
CREATE INDEX ix_auditoria_usuario ON auditoria (usuario_id);
CREATE INDEX ix_auditoria_entidad ON auditoria (entidad, entidad_id);
CREATE TRIGGER tg_auditoria_solo_insercion
  BEFORE UPDATE OR DELETE ON auditoria
  FOR EACH ROW EXECUTE FUNCTION fn_bloquear_modificacion();

-- -----------------------------------------------------------------------------
-- alertas_enviadas (P0) · una fila por cruce de umbral; evento_id evita duplicados
-- -----------------------------------------------------------------------------
CREATE TABLE alertas_enviadas (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  evento_id      uuid         NOT NULL,
  producto_id    bigint       NOT NULL REFERENCES productos (id),
  movimiento_id  bigint       REFERENCES movimientos (id),
  saldo          integer      NOT NULL,
  umbral         integer      NOT NULL,
  estado         varchar(10)  NOT NULL DEFAULT 'PENDIENTE',
  intentos       integer      NOT NULL DEFAULT 0,
  ultimo_error   varchar(200),
  creado_en      timestamptz  NOT NULL DEFAULT now(),
  enviado_en     timestamptz,
  CONSTRAINT uq_alertas_evento UNIQUE (evento_id),
  CONSTRAINT ck_alertas_estado CHECK (estado IN ('PENDIENTE', 'ENVIADA', 'FALLIDA')),
  CONSTRAINT ck_alertas_intentos CHECK (intentos >= 0),
  CONSTRAINT ck_alertas_enviada CHECK ((estado = 'ENVIADA') = (enviado_en IS NOT NULL))
);
CREATE INDEX ix_alertas_producto ON alertas_enviadas (producto_id);
CREATE INDEX ix_alertas_movimiento ON alertas_enviadas (movimiento_id);
CREATE INDEX ix_alertas_pendientes ON alertas_enviadas (estado) WHERE estado <> 'ENVIADA';

-- -----------------------------------------------------------------------------
-- pedidos (P1) · BORRADOR → APROBADO → ENVIADO → CONFIRMADO | CANCELADO
-- Un reintento con otro proveedor es un pedido nuevo enlazado al anterior.
-- -----------------------------------------------------------------------------
CREATE TABLE pedidos (
  id                      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  proveedor_id            bigint       NOT NULL REFERENCES proveedores (id),
  estado                  varchar(12)  NOT NULL DEFAULT 'BORRADOR',
  numero_intento          integer      NOT NULL DEFAULT 1,
  pedido_anterior_id      bigint       REFERENCES pedidos (id),
  creado_por              bigint       NOT NULL REFERENCES usuarios (id),
  aprobado_por            bigint       REFERENCES usuarios (id),
  fecha_creacion          timestamptz  NOT NULL DEFAULT now(),
  fecha_aprobacion        timestamptz,
  fecha_envio             timestamptz,
  fecha_respuesta         timestamptz,
  fecha_entrega_estimada  date,
  motivo_cancelacion      varchar(300),
  CONSTRAINT ck_pedidos_estado CHECK (estado IN ('BORRADOR', 'APROBADO', 'ENVIADO', 'CONFIRMADO', 'CANCELADO')),
  CONSTRAINT ck_pedidos_intento CHECK (numero_intento >= 1),
  CONSTRAINT ck_pedidos_reintento CHECK ((numero_intento = 1) = (pedido_anterior_id IS NULL)),
  CONSTRAINT uq_pedidos_anterior UNIQUE (pedido_anterior_id),
  CONSTRAINT ck_pedidos_aprobacion CHECK (
    estado NOT IN ('APROBADO', 'ENVIADO', 'CONFIRMADO')
    OR (aprobado_por IS NOT NULL AND fecha_aprobacion IS NOT NULL)
  ),
  CONSTRAINT ck_pedidos_envio CHECK (estado NOT IN ('ENVIADO', 'CONFIRMADO') OR fecha_envio IS NOT NULL),
  CONSTRAINT ck_pedidos_confirmacion CHECK (estado <> 'CONFIRMADO' OR fecha_respuesta IS NOT NULL),
  CONSTRAINT ck_pedidos_cancelacion CHECK (estado <> 'CANCELADO' OR length(btrim(coalesce(motivo_cancelacion, ''))) > 0),
  CONSTRAINT ck_pedidos_orden_fechas CHECK (
    (fecha_aprobacion IS NULL OR fecha_aprobacion >= fecha_creacion)
    AND (fecha_envio IS NULL OR fecha_aprobacion IS NULL OR fecha_envio >= fecha_aprobacion)
    AND (fecha_respuesta IS NULL OR fecha_envio IS NULL OR fecha_respuesta >= fecha_envio)
  )
);
CREATE INDEX ix_pedidos_proveedor ON pedidos (proveedor_id);
CREATE INDEX ix_pedidos_estado ON pedidos (estado);
CREATE INDEX ix_pedidos_creado_por ON pedidos (creado_por);
CREATE INDEX ix_pedidos_aprobado_por ON pedidos (aprobado_por);
COMMENT ON COLUMN pedidos.fecha_respuesta IS 'Respuesta del proveedor (entrada del proceso). KPI 4 = respuesta - envío.';

-- -----------------------------------------------------------------------------
-- pedido_detalles (P1)
-- -----------------------------------------------------------------------------
CREATE TABLE pedido_detalles (
  id                   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  pedido_id            bigint  NOT NULL REFERENCES pedidos (id),
  producto_id          bigint  NOT NULL REFERENCES productos (id),
  cantidad_sugerida    integer,
  cantidad_solicitada  integer NOT NULL,
  CONSTRAINT uq_pedido_detalles_producto UNIQUE (pedido_id, producto_id),
  CONSTRAINT ck_pedido_detalles_sugerida CHECK (cantidad_sugerida IS NULL OR cantidad_sugerida >= 0),
  CONSTRAINT ck_pedido_detalles_solicitada CHECK (cantidad_solicitada > 0)
);
CREATE INDEX ix_pedido_detalles_producto ON pedido_detalles (producto_id);
COMMENT ON COLUMN pedido_detalles.cantidad_sugerida IS 'NULL cuando el producto tiene datos insuficientes (cantidad manual del propietario).';
