"""Formato único de errores de la API.

Siempre: {"error": {"codigo", "mensaje", "campos"}}. Un 500 nunca muestra trazas,
consultas ni credenciales: el detalle va al log con una referencia que también
recibe el cliente, para poder encontrarlo.
"""

import logging

from flask import g, jsonify, redirect, request, url_for
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import HTTPException

log = logging.getLogger(__name__)

_CODIGOS_HTTP = {
    400: ("VALIDACION", "La solicitud no es válida."),
    401: ("NO_AUTENTICADO", "Debes iniciar sesión."),
    403: ("SIN_PERMISO", "No tienes permiso para esta acción."),
    404: ("NO_ENCONTRADO", "El recurso no existe."),
    405: ("METODO_NO_PERMITIDO", "Método no permitido en esta ruta."),
    409: ("CONFLICTO", "La operación choca con una regla de negocio."),
}


class ApiError(Exception):
    """Error de negocio o de validación que se devuelve tal cual al cliente."""

    def __init__(self, status: int, codigo: str, mensaje: str, campos: dict | None = None):
        super().__init__(mensaje)
        self.status = status
        self.codigo = codigo
        self.mensaje = mensaje
        self.campos = campos or {}


def respuesta_error(status: int, codigo: str, mensaje: str, campos: dict | None = None):
    cuerpo = {"error": {"codigo": codigo, "mensaje": mensaje, "campos": campos or {}}}
    if status >= 500:
        cuerpo["error"]["referencia"] = getattr(g, "request_id", None)
    return jsonify(cuerpo), status


def es_api() -> bool:
    return request.path.startswith("/api/") or request.path == "/api"


def registrar_manejadores(app) -> None:
    @app.errorhandler(ApiError)
    def _api_error(e: ApiError):
        return respuesta_error(e.status, e.codigo, e.mensaje, e.campos)

    @app.errorhandler(CSRFError)
    def _csrf(e: CSRFError):
        if es_api():
            return respuesta_error(400, "VALIDACION", "Token CSRF inválido o ausente.", {"csrf": "invalido"})
        # En formularios HTML: volver al login con un mensaje genérico
        return redirect(url_for("auth.login", error="sesion"))

    @app.errorhandler(HTTPException)
    def _http(e: HTTPException):
        if not es_api():
            return e
        codigo, mensaje = _CODIGOS_HTTP.get(e.code, ("ERROR_HTTP", e.name))
        return respuesta_error(e.code, codigo, mensaje)

    @app.errorhandler(Exception)
    def _inesperado(e: Exception):
        log.exception("Error no controlado (ref=%s) en %s %s", getattr(g, "request_id", "-"), request.method, request.path)
        if es_api():
            return respuesta_error(500, "ERROR_INTERNO", "Ocurrió un error interno. Intenta de nuevo o avisa al administrador.")
        return "Ocurrió un error interno.", 500
