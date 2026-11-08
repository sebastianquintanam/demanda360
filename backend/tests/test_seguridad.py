"""Controles transversales: CSRF en la API, errores 500 sin trazas, configuración segura."""

import pytest
from flask import Blueprint

from app import create_app
from app.config import TestConfig, validar_config
from app.security import requiere_sesion
from tests.conftest import aislar_usuario_por_peticion

_bp = Blueprint("pruebas_internas", __name__, url_prefix="/api/_pruebas")


@_bp.post("/eco")
@requiere_sesion
def _eco():
    return {"ok": True}


@_bp.get("/explota")
def _explota():
    raise RuntimeError("detalle interno: SELECT * FROM usuarios; clave=secreta")


@pytest.fixture(scope="module")
def app(app):
    """App propia de este módulo con dos rutas de prueba (Flask no deja agregar
    rutas a una app que ya atendió solicitudes)."""
    propia = create_app(TestConfig)
    propia.register_blueprint(_bp)
    aislar_usuario_por_peticion(propia)
    return propia


def test_error_500_sin_trazas_y_con_referencia(client):
    r = client.get("/api/_pruebas/explota")
    assert r.status_code == 500
    cuerpo = r.get_data(as_text=True)
    assert "SELECT" not in cuerpo and "secreta" not in cuerpo and "Traceback" not in cuerpo
    err = r.get_json()["error"]
    assert err["codigo"] == "ERROR_INTERNO"
    assert err["referencia"] == r.headers["X-Request-ID"]


def test_post_api_sin_csrf_rechazado(app, client_trabajador):
    app.config["WTF_CSRF_ENABLED"] = True
    try:
        r = client_trabajador.post("/api/_pruebas/eco", json={})
        assert r.status_code == 400
        assert r.get_json()["error"]["campos"] == {"csrf": "invalido"}
    finally:
        app.config["WTF_CSRF_ENABLED"] = False


def test_post_api_con_csrf_en_cabecera_aceptado(app, client_trabajador):
    app.config["WTF_CSRF_ENABLED"] = True
    try:
        html = client_trabajador.get("/dashboard").get_data(as_text=True)
        token = html.split('<meta name="csrf-token" content="')[1].split('"')[0]
        r = client_trabajador.post("/api/_pruebas/eco", json={}, headers={"X-CSRFToken": token})
        assert r.status_code == 200
    finally:
        app.config["WTF_CSRF_ENABLED"] = False


@pytest.mark.parametrize("clave", ["", "corta", "cambiar-por-un-secreto-largo-pero-de-ejemplo-xx"])
def test_secret_key_debil_impide_arrancar(clave):
    with pytest.raises(RuntimeError):
        validar_config({"SECRET_KEY": clave})


def test_secret_key_fuerte_permite_arrancar():
    validar_config({"SECRET_KEY": "x" * 48})


def test_post_api_sin_sesion_con_csrf_activo_responde_401(app, client):
    """Sesión vencida: 401 (la pantalla lleva al login), no 400 de CSRF."""
    app.config["WTF_CSRF_ENABLED"] = True
    try:
        r = client.post("/api/_pruebas/eco", json={})
        assert r.status_code == 401
        assert r.get_json()["error"]["codigo"] == "NO_AUTENTICADO"
    finally:
        app.config["WTF_CSRF_ENABLED"] = False
