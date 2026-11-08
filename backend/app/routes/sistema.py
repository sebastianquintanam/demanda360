"""Rutas transversales: estado del sistema y consulta de la bitácora."""

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import text

from ..errors import ApiError
from ..extensions import db
from ..models import Auditoria, Usuario
from ..security import ROL_PROPIETARIO, requiere_rol

bp = Blueprint("sistema", __name__, url_prefix="/api")


@bp.get("/health")
def health():
    """Público. No revela versiones, host ni credenciales."""
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify(estado="ok", bd="ok")
    except Exception:  # noqa: BLE001 - se informa como degradado, el detalle va al log
        current_app.logger.exception("Health: la base no responde")
        db.session.rollback()
        return jsonify(estado="degradado", bd="error"), 503


@bp.get("/auditoria")
@requiere_rol(ROL_PROPIETARIO, mensaje="Solo un propietario puede consultar la auditoría.")
def listar_auditoria():
    try:
        limite = int(request.args.get("limite", 50))
    except ValueError:
        raise ApiError(400, "VALIDACION", "limite debe ser un número entero.", {"limite": "entero"})
    if not 1 <= limite <= 200:
        raise ApiError(400, "VALIDACION", "limite debe estar entre 1 y 200.", {"limite": "rango"})

    filas = db.session.execute(
        db.select(Auditoria, Usuario.usuario)
        .outerjoin(Usuario, Usuario.id == Auditoria.usuario_id)
        .order_by(Auditoria.fecha_hora.desc(), Auditoria.id.desc())
        .limit(limite)
    ).all()
    return jsonify(
        registros=[
            {
                "id": a.id,
                "fecha_hora": a.fecha_hora.isoformat(),
                "usuario": usuario,
                "accion": a.accion,
                "entidad": a.entidad,
                "entidad_id": a.entidad_id,
                "detalle": a.detalle,
            }
            for a, usuario in filas
        ]
    )
