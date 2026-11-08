from sqlalchemy import FetchedValue

from ..extensions import db


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)


class Proveedor(db.Model):
    __tablename__ = "proveedores"

    id = db.Column(db.BigInteger, primary_key=True)
    codigo = db.Column(db.String(20), nullable=False, unique=True)
    nombre = db.Column(db.String(120), nullable=False)
    plazo_entrega_dias = db.Column(db.Integer, nullable=False)
    contacto = db.Column(db.String(120))
    activo = db.Column(db.Boolean, nullable=False, server_default=FetchedValue())
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, server_default=FetchedValue())


class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.BigInteger, primary_key=True)
    sku = db.Column(db.String(30), nullable=False, unique=True)
    nombre = db.Column(db.String(150), nullable=False)
    categoria_id = db.Column(db.BigInteger, db.ForeignKey("categorias.id"), nullable=False)
    proveedor_id = db.Column(db.BigInteger, db.ForeignKey("proveedores.id"), nullable=False)
    marca = db.Column(db.String(80))
    presentacion = db.Column(db.String(60), nullable=False)
    unidad_medida = db.Column(db.String(20), nullable=False)
    costo_compra = db.Column(db.Numeric(12, 2), nullable=False)
    precio_venta = db.Column(db.Numeric(12, 2), nullable=False)
    umbral_reposicion = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, server_default=FetchedValue())
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, server_default=FetchedValue())

    categoria = db.relationship(Categoria, lazy="joined")
    proveedor = db.relationship(Proveedor, lazy="joined")

    # Ojo: no hay atributo "saldo". Se calcula en la vista vw_saldos (etapa 2).
