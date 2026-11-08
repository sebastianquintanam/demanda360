"""Alerta de stock crítico (plan, sección 5) con n8n simulado.

  · Solo la venta que cruza el umbral crea alerta; las siguientes bajo el umbral no.
  · ENVIADA solo si n8n responde 200 con ok = true.
  · Con n8n caído la venta se guarda y la alerta queda FALLIDA; el reintento la envía.
"""

import uuid

import pytest
import requests
from sqlalchemy import text

from app.services import alertas

TOKEN = "token-de-prueba-n8n"


class RespuestaFalsa:
    def __init__(self, status, cuerpo):
        self.status_code = status
        self._cuerpo = cuerpo

    def json(self):
        if self._cuerpo is None:
            raise ValueError("sin JSON")
        return self._cuerpo


class N8nFalso:
    """Reemplaza requests.post y guarda lo que recibió."""

    def __init__(self):
        self.llamadas = []
        self.modo = "ok"

    def __call__(self, url, json=None, headers=None, timeout=None):
        self.llamadas.append({"url": url, "json": json, "headers": headers, "timeout": timeout})
        if self.modo == "ok":
            return RespuestaFalsa(200, {"ok": True, "estado": "ENVIADA", "evento_id": json["evento_id"]})
        if self.modo == "smtp_falla":
            return RespuestaFalsa(502, {"ok": False, "error": "SMTP no disponible"})
        if self.modo == "200_sin_ok":
            return RespuestaFalsa(200, None)
        if self.modo == "lento":
            raise requests.Timeout()
        raise requests.ConnectionError("n8n apagado")


@pytest.fixture
def n8n(app, monkeypatch):
    falso = N8nFalso()
    monkeypatch.setattr(alertas.requests, "post", falso)
    monkeypatch.setitem(app.config, "N8N_WEBHOOK_URL", "http://n8n:5678/webhook/alerta-stock-critico")
    monkeypatch.setitem(app.config, "N8N_WEBHOOK_TOKEN", TOKEN)
    return falso


@pytest.fixture
def producto_con_5(db, usuarios, client_trabajador):
    """Producto con umbral 3 y saldo 5."""
    db.session.execute(text("""
        INSERT INTO categorias (nombre) VALUES ('Esmaltes');
        INSERT INTO proveedores (codigo, nombre, plazo_entrega_dias) VALUES ('PRV-1', 'Proveedor (ficticio)', 3);
        INSERT INTO productos (sku, nombre, categoria_id, proveedor_id, presentacion, unidad_medida,
                               costo_compra, precio_venta, umbral_reposicion)
        VALUES ('ESM-WH-01', 'Esmalte blanco galón', 1, 1, 'Galón', 'galon', 52000, 68000, 3);
    """))
    db.session.commit()
    r = client_trabajador.post("/api/conteos", json={"producto_id": 1, "cantidad_contada": 5, "origen_ref": "c-1"})
    assert r.status_code == 201
    return 1


def _venta(cliente, entregada):
    r = cliente.post("/api/ventas", json={"producto_id": 1, "cantidad_solicitada": entregada,
                                          "cantidad_entregada": entregada, "origen_ref": str(uuid.uuid4())})
    assert r.status_code == 201, r.get_json()
    return r.get_json()


def _alertas(db):
    return [dict(f) for f in db.session.execute(text("SELECT * FROM alertas_enviadas ORDER BY id")).mappings()]


def test_solo_la_venta_que_cruza_el_umbral_alerta(client_trabajador, producto_con_5, n8n, db):
    assert _venta(client_trabajador, 1)["alerta"] is None          # 5 → 4: sigue sobre el umbral
    cruce = _venta(client_trabajador, 2)                            # 4 → 2: cruza el umbral 3
    assert cruce["alerta"]["estado"] == "ENVIADA"
    assert cruce["producto"]["estado"] == "CRITICO"
    assert _venta(client_trabajador, 1)["alerta"] is None          # 2 → 1: ya estaba bajo el umbral
    assert len(n8n.llamadas) == 1 and len(_alertas(db)) == 1


def test_evento_enviado_a_n8n_cumple_el_contrato(client_trabajador, producto_con_5, n8n):
    cruce = _venta(client_trabajador, 3)                            # 5 → 2
    llamada = n8n.llamadas[0]
    assert llamada["headers"] == {"X-Demanda360-Token": TOKEN}
    assert llamada["timeout"] == 10
    evento = llamada["json"]
    assert set(evento) == {"evento_id", "tipo", "ocurrido_en", "origen_datos", "producto"}
    assert (evento["tipo"], evento["origen_datos"]) == ("STOCK_CRITICO", "SIMULADO")
    assert evento["evento_id"] == cruce["alerta"]["evento_id"]
    assert evento["producto"] == {"sku": "ESM-WH-01", "nombre": "Esmalte blanco galón", "saldo": 2,
                                  "umbral": 3, "plazo_entrega_dias": 3}
    assert evento["ocurrido_en"].endswith("-05:00")


@pytest.mark.parametrize("modo,error", [
    ("apagado", "No se pudo conectar con n8n"),
    ("smtp_falla", "n8n respondió 502: SMTP no disponible"),
    ("200_sin_ok", "n8n respondió 200"),
    ("lento", "n8n no respondió a tiempo"),
])
def test_si_n8n_falla_la_venta_se_guarda_y_la_alerta_queda_fallida(client_trabajador, producto_con_5, n8n, db,
                                                                   modo, error):
    n8n.modo = modo
    cruce = _venta(client_trabajador, 3)
    assert cruce["alerta"]["estado"] == "FALLIDA"
    assert cruce["producto"]["saldo_actual"] == 2                     # la venta quedó
    a = _alertas(db)[0]
    assert (a["estado"], a["intentos"], a["enviado_en"]) == ("FALLIDA", 1, None)
    assert a["ultimo_error"].startswith(error)


def test_reintento_con_el_mismo_evento_id(app, client_trabajador, producto_con_5, n8n, db):
    n8n.modo = "apagado"
    cruce = _venta(client_trabajador, 3)
    n8n.modo = "ok"
    salida = app.test_cli_runner().invoke(args=["reintentar-alertas"]).output
    assert "ENVIADA" in salida
    a = _alertas(db)[0]
    assert (a["estado"], a["intentos"], a["ultimo_error"]) == ("ENVIADA", 2, None)
    assert n8n.llamadas[-1]["json"]["evento_id"] == cruce["alerta"]["evento_id"]
    # Una alerta ENVIADA nunca se reenvía
    assert "No hay alertas" in app.test_cli_runner().invoke(args=["reintentar-alertas"]).output
    assert len(n8n.llamadas) == 2


def test_maximo_tres_intentos(app, client_trabajador, producto_con_5, n8n, db):
    n8n.modo = "apagado"
    _venta(client_trabajador, 3)
    for _ in range(4):
        app.test_cli_runner().invoke(args=["reintentar-alertas"])
    assert _alertas(db)[0]["intentos"] == 3
    assert len(n8n.llamadas) == 3


def test_sin_webhook_configurado_queda_fallida(app, client_trabajador, producto_con_5, db, monkeypatch):
    monkeypatch.setitem(app.config, "N8N_WEBHOOK_URL", "")
    cruce = _venta(client_trabajador, 3)
    assert cruce["alerta"]["estado"] == "FALLIDA"
    assert "sin configurar" in _alertas(db)[0]["ultimo_error"]


def test_la_alerta_queda_en_la_auditoria(client_trabajador, producto_con_5, n8n, db):
    _venta(client_trabajador, 3)
    acciones = list(db.session.execute(text("SELECT accion FROM auditoria ORDER BY id")).scalars())
    assert acciones[-2:] == ["VENTA_REGISTRADA", "ALERTA_CREADA"]
