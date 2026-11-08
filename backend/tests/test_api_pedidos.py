"""P1 · sugeridos y pedidos: permisos, transiciones (409) y KPI 4–5 alimentados desde la app."""

import json
from pathlib import Path

import pytest
from sqlalchemy import text

MOCKS = Path(__file__).resolve().parents[2] / "frontend" / "static" / "mock"


def _mock(nombre):
    return json.loads((MOCKS / nombre).read_text(encoding="utf-8"))


@pytest.fixture
def demo(app, usuarios):
    r = app.test_cli_runner().invoke(args=["cargar-demo"])
    assert r.exit_code == 0, r.output


def _crear(cliente, proveedor_id=1, lineas=((1, 24),), **extra):
    return cliente.post("/api/pedidos", json={
        "proveedor_id": proveedor_id,
        "detalles": [{"producto_id": p, "cantidad_solicitada": c} for p, c in lineas], **extra})


def _estado(cliente, pedido_id, estado, **extra):
    return cliente.post(f"/api/pedidos/{pedido_id}/estado", json={"estado": estado, **extra})


# --- Sugeridos ---------------------------------------------------------------------------

def test_sugeridos_igual_al_mock(client_propietario, demo):
    real, mock = client_propietario.get("/api/sugeridos").get_json(), _mock("sugeridos.json")
    for campo in ("corte", "origen_datos", "cobertura_dias", "referencias_prioritarias", "total_sugerido"):
        assert real[campo] == mock[campo], campo
    for r, m in zip(real["productos"], mock["productos"], strict=True):
        assert {k: r[k] for k in m} == m
        assert r["proveedor"] and r["proveedor_id"]


def test_sugeridos_con_otra_cobertura(client_propietario, demo):
    r = client_propietario.get("/api/sugeridos?cobertura=7").get_json()
    laca = next(p for p in r["productos"] if p["sku"] == "LAC-BP-01")
    assert (r["cobertura_dias"], laca["sugerido"]) == (7, 12)          # techo(51/30 × 7) = 12
    assert client_propietario.get("/api/sugeridos?cobertura=0").status_code == 400


def test_trabajador_no_ve_sugeridos(client_trabajador, demo):
    r = client_trabajador.get("/api/sugeridos")
    assert r.status_code == 403 and r.get_json()["error"]["codigo"] == "SIN_PERMISO"


# --- Crear y listar -------------------------------------------------------------------------

def test_crear_borrador_calcula_la_sugerida_en_el_servidor(client_trabajador, demo, db):
    r = _crear(client_trabajador, lineas=((1, 30), (6, 2)), cantidad_sugerida=999)
    assert r.status_code == 201
    p = r.get_json()
    for clave in _mock("pedido_creado.json"):
        assert clave in p
    assert (p["estado"], p["numero_intento"]) == ("BORRADOR", 1)
    assert [(d["sku"], d["cantidad_sugerida"], d["cantidad_solicitada"]) for d in p["detalles"]] == [
        ("LAC-BP-01", 24, 30), ("LAC-TR-01", None, 2)]                 # datos insuficientes → manual
    assert db.session.execute(text("SELECT accion FROM auditoria ORDER BY id DESC LIMIT 1")).scalar() == "PEDIDO_CREADO"


@pytest.mark.parametrize("cuerpo,campo", [
    ({"proveedor_id": 99, "detalles": [{"producto_id": 1, "cantidad_solicitada": 1}]}, "proveedor_id"),
    ({"proveedor_id": 1, "detalles": []}, "detalles"),
    ({"proveedor_id": 1, "detalles": [{"producto_id": 1, "cantidad_solicitada": 0}]}, "cantidad_solicitada"),
    ({"proveedor_id": 1, "detalles": [{"producto_id": 77, "cantidad_solicitada": 1}]}, "detalles[0].producto_id"),
    ({"proveedor_id": 1, "detalles": [{"producto_id": 1, "cantidad_solicitada": 1},
                                      {"producto_id": 1, "cantidad_solicitada": 2}]}, "detalles[1].producto_id"),
])
def test_borrador_invalido_400(client_propietario, demo, cuerpo, campo):
    r = client_propietario.post("/api/pedidos", json=cuerpo)
    assert r.status_code == 400 and campo in r.get_json()["error"]["campos"]


def test_listar_pedidos(client_trabajador, demo):
    _crear(client_trabajador)
    cuerpo = client_trabajador.get("/api/pedidos").get_json()
    assert cuerpo["origen_datos"] == "SIMULADO"
    assert len(cuerpo["pedidos"]) == 6                                  # 5 de la demo + el nuevo
    assert set(_mock("pedidos.json")["pedidos"][0]) <= set(cuerpo["pedidos"][0])
    enviado = next(p for p in cuerpo["pedidos"] if p["estado"] == "ENVIADO")
    assert enviado["horas_esperando"] > 0


# --- Aprobación y estados ----------------------------------------------------------------------

def test_trabajador_no_aprueba_403(client_trabajador, demo):
    pid = _crear(client_trabajador).get_json()["id"]
    r = client_trabajador.post(f"/api/pedidos/{pid}/aprobar")
    assert r.status_code == 403
    assert r.get_json() == _mock("error_403_sin_permiso.json")
    assert _estado(client_trabajador, pid, "CANCELADO", motivo_cancelacion="No va").status_code == 403


def test_ciclo_completo(client_trabajador, client_propietario, demo, db):
    pid = _crear(client_trabajador).get_json()["id"]
    a = client_propietario.post(f"/api/pedidos/{pid}/aprobar").get_json()
    assert a["estado"] == "APROBADO" and a["fecha_aprobacion"]
    e = _estado(client_propietario, pid, "ENVIADO").get_json()
    assert e["estado"] == "ENVIADO" and e["fecha_envio"] and e["horas_esperando"] is not None
    c = _estado(client_propietario, pid, "CONFIRMADO").get_json()
    assert c["estado"] == "CONFIRMADO" and c["fecha_respuesta"] and c["fecha_entrega_estimada"]
    acciones = list(db.session.execute(text(
        "SELECT accion FROM auditoria WHERE entidad = 'pedidos' ORDER BY id")).scalars())
    assert acciones == ["PEDIDO_CREADO", "PEDIDO_APROBADO", "PEDIDO_ENVIADO", "PEDIDO_CONFIRMADO"]
    aprobado_por = db.session.execute(text(f"SELECT aprobado_por FROM pedidos WHERE id = {pid}")).scalar()
    assert aprobado_por == 1                                           # el propietario queda registrado


@pytest.mark.parametrize("pasos,destino", [
    ([], "ENVIADO"),                    # borrador sin aprobar no se envía
    ([], "CONFIRMADO"),
    (["aprobar"], "CONFIRMADO"),        # aprobado sin enviar no se confirma
    (["aprobar", "ENVIADO", "CONFIRMADO"], "CANCELADO"),
])
def test_transicion_invalida_409(client_propietario, demo, pasos, destino):
    pid = _crear(client_propietario).get_json()["id"]
    for paso in pasos:
        if paso == "aprobar":
            client_propietario.post(f"/api/pedidos/{pid}/aprobar")
        else:
            _estado(client_propietario, pid, paso)
    r = _estado(client_propietario, pid, destino, motivo_cancelacion="Motivo de prueba")
    assert r.status_code == 409 and r.get_json()["error"]["codigo"] == "TRANSICION_INVALIDA"


def test_aprobar_dos_veces_409(client_propietario, demo):
    pid = _crear(client_propietario).get_json()["id"]
    assert client_propietario.post(f"/api/pedidos/{pid}/aprobar").status_code == 200
    assert client_propietario.post(f"/api/pedidos/{pid}/aprobar").status_code == 409
    assert client_propietario.post("/api/pedidos/999/aprobar").status_code == 404


def test_cancelar_exige_motivo(client_propietario, demo):
    pid = _crear(client_propietario).get_json()["id"]
    r = _estado(client_propietario, pid, "CANCELADO")
    assert r.status_code == 400 and "motivo_cancelacion" in r.get_json()["error"]["campos"]


def test_reintento_con_otro_proveedor(client_propietario, demo):
    pid = _crear(client_propietario, proveedor_id=2, lineas=((2, 10),)).get_json()["id"]
    client_propietario.post(f"/api/pedidos/{pid}/aprobar")
    _estado(client_propietario, pid, "ENVIADO")
    r = _estado(client_propietario, pid, "CANCELADO", motivo_cancelacion="Sin respuesta en 48 horas",
                reintentar_con_proveedor_id=1)
    assert r.status_code == 200
    cuerpo = r.get_json()
    assert cuerpo["estado"] == "CANCELADO"
    nuevo = cuerpo["reintento"]
    assert (nuevo["estado"], nuevo["numero_intento"], nuevo["pedido_anterior_id"], nuevo["proveedor_id"]) == (
        "APROBADO", 2, pid, 1)
    assert [(d["sku"], d["cantidad_solicitada"]) for d in nuevo["detalles"]] == [("LAC-BP-02", 10)]
    assert client_propietario.get("/api/pedidos").get_json()["pedidos"][1]["reintento_id"] == nuevo["id"]
    # mismo proveedor → 400
    otro = _crear(client_propietario).get_json()["id"]
    r = _estado(client_propietario, otro, "CANCELADO", motivo_cancelacion="Prueba", reintentar_con_proveedor_id=1)
    assert r.status_code == 400


def test_kpi_4_y_5_desde_la_app(client_propietario, demo, db):
    """Un pedido confirmado en el primer intento y otro tras un reintento, hoy."""
    def ciclo(proveedor, cancelar_con=None):
        pid = _crear(client_propietario, proveedor_id=proveedor).get_json()["id"]
        client_propietario.post(f"/api/pedidos/{pid}/aprobar")
        _estado(client_propietario, pid, "ENVIADO")
        if cancelar_con:
            pid = _estado(client_propietario, pid, "CANCELADO", motivo_cancelacion="Sin respuesta",
                          reintentar_con_proveedor_id=cancelar_con).get_json()["reintento"]["id"]
            _estado(client_propietario, pid, "ENVIADO")
        _estado(client_propietario, pid, "CONFIRMADO")

    ciclo(1)
    ciclo(2, cancelar_con=1)
    k5 = db.session.execute(text(
        "SELECT valor, numerador, denominador FROM fn_kpi_resumen(CURRENT_DATE) WHERE codigo = 'KPI5'")).one()
    assert (float(k5.valor), int(k5.numerador), k5.denominador) == (50.0, 1, 2)
    k4 = db.session.execute(text(
        "SELECT denominador, detalle FROM fn_kpi_resumen(CURRENT_DATE) WHERE codigo = 'KPI4'")).one()
    assert k4.denominador == 2 and "1 enviado(s) sin respuesta" in k4.detalle   # el cancelado sin respuesta
