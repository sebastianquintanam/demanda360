"""Autenticación y permisos por rol, verificados SIEMPRE en el backend.

Ocultar un botón en la pantalla no es un control: cada ruta protegida usa
@requiere_rol (o @requiere_sesion) y la API responde 401 / 403 en JSON.
"""

from functools import wraps
from urllib.parse import urlsplit

from flask import request
from flask_login import current_user

from .errors import ApiError

ROL_PROPIETARIO = "propietario"
ROL_TRABAJADOR = "trabajador"
ROLES = (ROL_PROPIETARIO, ROL_TRABAJADOR)


def requiere_sesion(fn):
    """Exige sesión iniciada. En /api responde 401 JSON (lo maneja login_manager)."""

    @wraps(fn)
    def envoltura(*args, **kwargs):
        if not current_user.is_authenticated:
            raise ApiError(401, "NO_AUTENTICADO", "Debes iniciar sesión.")
        return fn(*args, **kwargs)

    return envoltura


def requiere_rol(*roles: str, mensaje: str | None = None):
    """Exige sesión y uno de los roles indicados.

    Uso:
        @requiere_rol("propietario", mensaje="Solo un propietario puede aprobar pedidos.")
    """
    for rol in roles:
        if rol not in ROLES:
            raise ValueError(f"Rol desconocido: {rol}")

    def decorador(fn):
        @wraps(fn)
        def envoltura(*args, **kwargs):
            if not current_user.is_authenticated:
                raise ApiError(401, "NO_AUTENTICADO", "Debes iniciar sesión.")
            if current_user.rol not in roles:
                raise ApiError(403, "SIN_PERMISO", mensaje or "No tienes permiso para esta acción.")
            return fn(*args, **kwargs)

        return envoltura

    return decorador


def es_propietario() -> bool:
    return current_user.is_authenticated and current_user.rol == ROL_PROPIETARIO


def destino_seguro(destino: str | None, por_defecto: str) -> str:
    """Evita redirecciones abiertas: solo rutas internas como /dashboard."""
    if not destino:
        return por_defecto
    partes = urlsplit(destino)
    if partes.scheme or partes.netloc or not destino.startswith("/") or destino.startswith("//"):
        return por_defecto
    return destino


def ip_cliente() -> str:
    # No se guarda en la base (minimización); solo se usa en logs
    return request.remote_addr or "-"
