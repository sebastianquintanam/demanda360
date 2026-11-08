from sqlalchemy import FetchedValue
from sqlalchemy.dialects.postgresql import JSONB, UUID

from ..extensions import db


class Auditoria(db.Model):
    """Bitácora de solo inserción (un trigger impide UPDATE y DELETE)."""

    __tablename__ = "auditoria"

    id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuarios.id"))
    accion = db.Column(db.String(50), nullable=False)
    entidad = db.Column(db.String(50), nullable=False)
    entidad_id = db.Column(db.BigInteger)
    fecha_hora = db.Column(db.DateTime(timezone=True), nullable=False, server_default=FetchedValue())
    detalle = db.Column(JSONB, nullable=False, server_default=FetchedValue())


class AlertaEnviada(db.Model):
    __tablename__ = "alertas_enviadas"

    ESTADOS = ("PENDIENTE", "ENVIADA", "FALLIDA")

    id = db.Column(db.BigInteger, primary_key=True)
    evento_id = db.Column(UUID(as_uuid=True), nullable=False, unique=True)
    producto_id = db.Column(db.BigInteger, db.ForeignKey("productos.id"), nullable=False)
    movimiento_id = db.Column(db.BigInteger, db.ForeignKey("movimientos.id"))
    saldo = db.Column(db.Integer, nullable=False)
    umbral = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(10), nullable=False, server_default=FetchedValue())
    intentos = db.Column(db.Integer, nullable=False, server_default=FetchedValue())
    ultimo_error = db.Column(db.String(200))
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, server_default=FetchedValue())
    enviado_en = db.Column(db.DateTime(timezone=True))
