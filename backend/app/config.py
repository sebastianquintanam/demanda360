"""Configuración leída del entorno (.env). Ninguna credencial vive en el código."""

import os
from datetime import timedelta


def _database_url() -> str:
    """DATABASE_URL si existe; si no, se arma con las variables POSTGRES_* del .env.

    Así el mismo .env sirve dentro de Docker (DB_HOST=db) y en el Mac (DB_HOST=localhost).
    """
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    usuario = os.environ.get("POSTGRES_USER", "demanda360")
    clave = os.environ.get("POSTGRES_PASSWORD", "")
    host = os.environ.get("DB_HOST", "localhost")
    puerto = os.environ.get("DB_PORT", "5432")
    base = os.environ.get("POSTGRES_DB", "demanda360")
    return f"postgresql+psycopg://{usuario}:{clave}@{host}:{puerto}/{base}"


class Config:
    APP_ENV = os.environ.get("APP_ENV", "production")
    SECRET_KEY = os.environ.get("SECRET_KEY", "")

    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        # Toda la sesión de base en hora de Bogotá; 5 s máximo por consulta
        "connect_args": {"options": "-c timezone=America/Bogota -c statement_timeout=5000"},
    }

    # Sesión: cookie HttpOnly, SameSite=Lax, vence a las 8 horas
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    REMEMBER_COOKIE_DURATION = timedelta(hours=8)
    REMEMBER_COOKIE_HTTPONLY = True

    # CSRF: formularios y cabecera X-CSRFToken en los POST de /api
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # el token dura lo que dura la sesión

    # Integración con n8n (contrato en services/alertas.py). 10 s y no 3: Gmail tarda
    # ~2,5 s y con 3 s quedarían FALLIDAS alertas que sí se enviaron.
    N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL", "")
    N8N_WEBHOOK_TOKEN = os.environ.get("N8N_WEBHOOK_TOKEN", "")
    N8N_TIMEOUT_SEGUNDOS = 10

    # Todo el historial del MVP es simulado y se rotula así
    ORIGEN_DATOS = os.environ.get("ORIGEN_DATOS", "SIMULADO")


class TestConfig(Config):
    TESTING = True
    APP_ENV = "test"
    SECRET_KEY = "clave-solo-para-pruebas-no-usar-en-otro-lado"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL",
        _database_url().rsplit("/", 1)[0] + "/demanda360_test",
    )
    WTF_CSRF_ENABLED = False  # se reactiva en la prueba específica de CSRF


def validar_config(config) -> None:
    """Falla al arrancar si falta un secreto o si se dejó el valor de ejemplo."""
    if config.get("TESTING"):
        return
    clave = config.get("SECRET_KEY") or ""
    if len(clave) < 32 or clave.startswith("cambiar"):
        raise RuntimeError(
            "SECRET_KEY no está configurada. Genera una con: "
            "python3 -c \"import secrets; print(secrets.token_urlsafe(48))\" y ponla en .env"
        )
