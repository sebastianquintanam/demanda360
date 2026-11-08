"""App factory de Demanda360.

Flask valida y registra; PostgreSQL es la única fuente de datos; n8n solo avisa;
Power BI solo lee. Ningún otro componente guarda saldos.
"""

import logging
import os
import uuid
from pathlib import Path

from flask import Flask, g, request

from .config import Config, validar_config
from .extensions import csrf, db, login_manager

# backend/app -> repo/frontend
_FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


def create_app(config_object=Config) -> Flask:
    app = Flask(
        __name__,
        template_folder=str(_FRONTEND / "templates"),
        static_folder=str(_FRONTEND / "static"),
        static_url_path="/static",
    )
    app.config.from_object(config_object)
    app.json.sort_keys = False  # respuestas con el orden del contrato
    validar_config(app.config)
    _configurar_logs(app)

    @app.before_request
    def _api_sin_sesion_primero_401():
        """Se registra ANTES que CSRF: un POST a /api sin sesión (p. ej. sesión vencida)
        responde 401 y la pantalla lleva al login, en vez de un 400 de CSRF."""
        from flask_login import current_user

        from .errors import respuesta_error

        if (request.path.startswith("/api/") and request.method not in ("GET", "HEAD", "OPTIONS")
                and request.routing_exception is None  # ruta o método inexistente: 404 / 405
                and not current_user.is_authenticated):
            return respuesta_error(401, "NO_AUTENTICADO", "Debes iniciar sesión.")
        return None

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = None
    login_manager.session_protection = "strong"

    from . import models  # noqa: F401  (registra los mapeos)
    from .errors import es_api, registrar_manejadores, respuesta_error
    from .models import Usuario

    @login_manager.user_loader
    def cargar_usuario(user_id: str):
        return db.session.get(Usuario, int(user_id))

    @login_manager.unauthorized_handler
    def no_autenticado():
        from flask import redirect, url_for

        if es_api():
            return respuesta_error(401, "NO_AUTENTICADO", "Debes iniciar sesión.")
        return redirect(url_for("auth.login", next=request.path))

    from .routes import analitica, auth, inventario, pedidos, sistema, vistas

    app.register_blueprint(auth.bp)
    app.register_blueprint(sistema.bp)
    app.register_blueprint(inventario.bp)
    app.register_blueprint(analitica.bp)
    app.register_blueprint(pedidos.bp)
    app.register_blueprint(vistas.bp)
    registrar_manejadores(app)

    from .cli import registrar_comandos

    registrar_comandos(app)

    @app.before_request
    def _asignar_request_id():
        entrante = request.headers.get("X-Request-ID", "")
        g.request_id = entrante[:64] if entrante else uuid.uuid4().hex[:16]

    @app.after_request
    def _cabeceras(resp):
        resp.headers["X-Request-ID"] = g.get("request_id", "-")
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "same-origin"
        if request.path.startswith("/api/"):
            resp.headers["Cache-Control"] = "no-store"
        return resp

    @app.context_processor
    def _contexto_global():
        return {"origen_datos": app.config["ORIGEN_DATOS"]}

    return app


def _configurar_logs(app: Flask) -> None:
    nivel = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    app.logger.setLevel(nivel)
