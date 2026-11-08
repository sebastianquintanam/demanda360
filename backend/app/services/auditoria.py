"""Registro en la bitácora. Se llama DENTRO de la misma transacción de la operación:
si la operación se revierte, la fila de auditoría también (no hay auditoría huérfana)."""

from flask_login import current_user

from ..extensions import db
from ..models import Auditoria

_CLAVES_PROHIBIDAS = {"password", "clave", "password_hash", "token", "secret"}


def registrar(accion: str, entidad: str, entidad_id: int | None = None,
              detalle: dict | None = None, usuario_id: int | None = None) -> Auditoria:
    """Agrega una fila de auditoría a la sesión actual (no hace commit)."""
    detalle = {k: v for k, v in (detalle or {}).items() if k.lower() not in _CLAVES_PROHIBIDAS}
    if usuario_id is None and current_user and current_user.is_authenticated:
        usuario_id = current_user.id
    fila = Auditoria(usuario_id=usuario_id, accion=accion, entidad=entidad,
                     entidad_id=entidad_id, detalle=detalle)
    db.session.add(fila)
    return fila
