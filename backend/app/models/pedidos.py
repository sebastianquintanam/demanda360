from sqlalchemy import FetchedValue

from ..extensions import db


class Pedido(db.Model):
    __tablename__ = "pedidos"

    ESTADOS = ("BORRADOR", "APROBADO", "ENVIADO", "CONFIRMADO", "CANCELADO")

    id = db.Column(db.BigInteger, primary_key=True)
    proveedor_id = db.Column(db.BigInteger, db.ForeignKey("proveedores.id"), nullable=False)
    estado = db.Column(db.String(12), nullable=False, server_default=FetchedValue())
    numero_intento = db.Column(db.Integer, nullable=False, server_default=FetchedValue())
    pedido_anterior_id = db.Column(db.BigInteger, db.ForeignKey("pedidos.id"), unique=True)
    creado_por = db.Column(db.BigInteger, db.ForeignKey("usuarios.id"), nullable=False)
    aprobado_por = db.Column(db.BigInteger, db.ForeignKey("usuarios.id"))
    fecha_creacion = db.Column(db.DateTime(timezone=True), nullable=False, server_default=FetchedValue())
    fecha_aprobacion = db.Column(db.DateTime(timezone=True))
    fecha_envio = db.Column(db.DateTime(timezone=True))
    fecha_respuesta = db.Column(db.DateTime(timezone=True))
    fecha_entrega_estimada = db.Column(db.Date)
    motivo_cancelacion = db.Column(db.String(300))

    detalles = db.relationship("PedidoDetalle", back_populates="pedido", lazy="selectin")


class PedidoDetalle(db.Model):
    __tablename__ = "pedido_detalles"

    id = db.Column(db.BigInteger, primary_key=True)
    pedido_id = db.Column(db.BigInteger, db.ForeignKey("pedidos.id"), nullable=False)
    producto_id = db.Column(db.BigInteger, db.ForeignKey("productos.id"), nullable=False)
    cantidad_sugerida = db.Column(db.Integer)
    cantidad_solicitada = db.Column(db.Integer, nullable=False)

    pedido = db.relationship(Pedido, back_populates="detalles")
