from sqlalchemy import FetchedValue

from ..extensions import db


class ConteoFisico(db.Model):
    __tablename__ = "conteos_fisicos"

    id = db.Column(db.BigInteger, primary_key=True)
    producto_id = db.Column(db.BigInteger, db.ForeignKey("productos.id"), nullable=False)
    cantidad_contada = db.Column(db.Integer, nullable=False)
    fecha_hora = db.Column(db.DateTime(timezone=True), nullable=False, server_default=FetchedValue())
    usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuarios.id"), nullable=False)
    observaciones = db.Column(db.String(300))
    origen_ref = db.Column(db.String(64), unique=True)


class Movimiento(db.Model):
    __tablename__ = "movimientos"

    TIPOS = ("VENTA", "ENTRADA", "AJUSTE")

    id = db.Column(db.BigInteger, primary_key=True)
    producto_id = db.Column(db.BigInteger, db.ForeignKey("productos.id"), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha_hora = db.Column(db.DateTime(timezone=True), nullable=False, server_default=FetchedValue())
    usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuarios.id"), nullable=False)
    origen_ref = db.Column(db.String(64), nullable=False, unique=True)
    justificacion = db.Column(db.String(500))


class SolicitudCliente(db.Model):
    __tablename__ = "solicitudes_clientes"

    id = db.Column(db.BigInteger, primary_key=True)
    producto_id = db.Column(db.BigInteger, db.ForeignKey("productos.id"), nullable=False)
    cantidad_solicitada = db.Column(db.Integer, nullable=False)
    cantidad_entregada = db.Column(db.Integer, nullable=False)
    fecha_hora = db.Column(db.DateTime(timezone=True), nullable=False, server_default=FetchedValue())
    usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuarios.id"), nullable=False)
    movimiento_id = db.Column(db.BigInteger, db.ForeignKey("movimientos.id"), unique=True)
    solicitud_previa_id = db.Column(db.BigInteger, db.ForeignKey("solicitudes_clientes.id"))
    origen_ref = db.Column(db.String(64), nullable=False, unique=True)

    @property
    def no_atendida(self) -> int:
        return self.cantidad_solicitada - self.cantidad_entregada
