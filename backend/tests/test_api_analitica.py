"""Etapa 3 · /api/dashboard y /api/analisis/rotacion con los datos demo: deben devolver
lo mismo que los mocks del frontend (las cifras del Figma)."""

import json
from pathlib import Path

import pytest

MOCKS = Path(__file__).resolve().parents[2] / "frontend" / "static" / "mock"


def _mock(nombre):
    return json.loads((MOCKS / nombre).read_text(encoding="utf-8"))


@pytest.fixture
def demo(app, usuarios):
    r = app.test_cli_runner().invoke(args=["cargar-demo"])
    assert r.exit_code == 0, r.output


def test_dashboard_igual_al_mock(client_trabajador, demo):
    real, mock = client_trabajador.get("/api/dashboard").get_json(), _mock("dashboard.json")
    assert (real["corte"], real["periodo"], real["origen_datos"]) == (mock["corte"], mock["periodo"], "SIMULADO")
    for r, m in zip(real["kpis"], mock["kpis"], strict=True):
        assert set(r) == set(m)
        for campo in ("codigo", "nombre", "valor", "unidad", "numerador", "denominador", "meta"):
            assert r[campo] == m[campo], (m["codigo"], campo)
    assert real["criticos"] == mock["criticos"]
    assert real["inventario"] == mock["inventario"]


def test_rotacion_igual_al_mock(client_trabajador, demo):
    assert client_trabajador.get("/api/analisis/rotacion").get_json() == _mock("rotacion.json")


def test_productos_igual_al_mock(client_trabajador, demo):
    assert client_trabajador.get("/api/productos").get_json() == _mock("productos.json")


def test_detalle_de_producto_demo(client_trabajador, demo):
    cuerpo = client_trabajador.get("/api/productos/1").get_json()
    assert cuerpo["producto"] == _mock("producto_detalle.json")["producto"]
    assert cuerpo["ultimo_conteo"]["cantidad_contada"] == 0
    assert len(cuerpo["ultimos_movimientos"]) == 10


def test_venta_en_vivo_cambia_criticos_pero_no_kpi(client_trabajador, demo):
    antes = client_trabajador.get("/api/dashboard").get_json()
    # SEL-CA-01 (id 5): saldo 4, umbral 4 → vender 1 lo deja en 3, sigue CRÍTICO
    r = client_trabajador.post("/api/ventas", json={"producto_id": 5, "cantidad_solicitada": 1,
                                                    "cantidad_entregada": 1, "origen_ref": "demo-en-vivo-1"})
    assert r.status_code == 201
    despues = client_trabajador.get("/api/dashboard").get_json()
    assert despues["kpis"] == antes["kpis"]
    assert [c["saldo"] for c in despues["criticos"] if c["id"] == 5] == [3]


def test_corte_por_parametro(client_trabajador, demo):
    cuerpo = client_trabajador.get("/api/dashboard?corte=2026-09-15").get_json()
    assert cuerpo["corte"] == "2026-09-15" and cuerpo["periodo"]["desde"] == "2026-08-17"
    assert client_trabajador.get("/api/analisis/rotacion?corte=2026-09-15").get_json()["corte"] == "2026-09-15"


@pytest.mark.parametrize("corte", ["30-09-2026", "2026-13-01", "2999-01-01"])
def test_corte_invalido_400(client_trabajador, demo, corte):
    r = client_trabajador.get(f"/api/dashboard?corte={corte}")
    assert r.status_code == 400 and "corte" in r.get_json()["error"]["campos"]
