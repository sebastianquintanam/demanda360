"""Etapa 3 · API de inventario. Cubre los criterios de aceptación del backend (plan, sección 9)
y que cada respuesta tenga al menos los campos de su mock en frontend/static/mock/."""

import json
import uuid
from pathlib import Path

import pytest
from sqlalchemy import text

MOCKS = Path(__file__).resolve().parents[2] / "frontend" / "static" / "mock"


def _mock(nombre):
    return json.loads((MOCKS / nombre).read_text(encoding="utf-8"))


def _contar(db, tabla):
    return db.session.execute(text(f"SELECT count(*) FROM {tabla}")).scalar()


def _ref():
    return str(uuid.uuid4())


def _incluye_campos(respuesta: dict, mock: dict, ruta=""):
    """Todo campo del mock existe en la respuesta (la API puede traer más, nunca menos)."""
    for clave, valor in mock.items():
        assert clave in respuesta, f"Falta {ruta}{clave}"
        if isinstance(valor, dict) and isinstance(respuesta[clave], dict):
            _incluye_campos(respuesta[clave], valor, f"{ruta}{clave}.")


@pytest.fixture
def catalogo(db, usuarios):
    db.session.execute(text("""
        INSERT INTO categorias (nombre) VALUES ('Lacas');
        INSERT INTO proveedores (codigo, nombre, plazo_entrega_dias) VALUES ('PRV-1', 'Proveedor (ficticio)', 3);
    """))
    db.session.commit()


PRODUCTO = {"sku": "LAC-BP-01", "nombre": "Laca catalizada alto brillo galón", "categoria_id": 1,
            "proveedor_id": 1, "marca": "ColorNova (ficticia)", "presentacion": "Galón",
            "unidad_medida": "galon", "costo_compra": 85000, "precio_venta": 110000, "umbral_reposicion": 2}


@pytest.fixture
def producto(client_propietario, catalogo):
    r = client_propietario.post("/api/productos", json=PRODUCTO)
    assert r.status_code == 201, r.get_json()
    return r.get_json()["id"]


def _conteo(cliente, producto_id, cantidad):
    r = cliente.post("/api/conteos", json={"producto_id": producto_id, "cantidad_contada": cantidad,
                                           "origen_ref": _ref()})
    assert r.status_code == 201, r.get_json()
    return r.get_json()


def _venta(cliente, producto_id, solicitada, entregada, **extra):
    return cliente.post("/api/ventas", json={"producto_id": producto_id, "cantidad_solicitada": solicitada,
                                             "cantidad_entregada": entregada, "origen_ref": _ref(), **extra})


# --- Sin sesión / roles ---------------------------------------------------------------

@pytest.mark.parametrize("metodo,ruta", [
    ("get", "/api/productos"), ("get", "/api/productos/1"), ("get", "/api/catalogos"),
    ("post", "/api/productos"), ("post", "/api/conteos"), ("post", "/api/ventas"),
    ("post", "/api/movimientos"), ("get", "/api/dashboard"), ("get", "/api/analisis/rotacion"),
])
def test_rutas_sin_sesion_responden_401(client, metodo, ruta):
    r = getattr(client, metodo)(ruta, json={})
    assert r.status_code == 401
    assert r.get_json()["error"]["codigo"] == "NO_AUTENTICADO"


def test_trabajador_no_crea_productos(client_trabajador, catalogo):
    r = client_trabajador.post("/api/productos", json=PRODUCTO)
    assert r.status_code == 403
    assert r.get_json()["error"]["mensaje"] == "Solo un propietario puede crear productos."


# --- Productos -------------------------------------------------------------------------

def test_crear_producto_201_con_forma_del_mock(client_propietario, catalogo, db):
    r = client_propietario.post("/api/productos", json={**PRODUCTO, "sku": " lac-bp-03 "})
    assert r.status_code == 201
    cuerpo = r.get_json()
    _incluye_campos(cuerpo, _mock("producto_creado.json"))
    assert (cuerpo["sku"], cuerpo["saldo"], cuerpo["estado"]) == ("LAC-BP-03", None, "SIN_CONTEO")
    assert cuerpo["costo_compra"] == 85000 and isinstance(cuerpo["costo_compra"], int)
    accion = db.session.execute(text("SELECT accion FROM auditoria ORDER BY id DESC LIMIT 1")).scalar()
    assert accion == "PRODUCTO_CREADO"


def test_sku_repetido_409(client_propietario, producto):
    r = client_propietario.post("/api/productos", json={**PRODUCTO, "sku": "lac-bp-01"})
    assert r.status_code == 409
    assert r.get_json() == _mock("error_409_sku.json")


@pytest.mark.parametrize("campo,valor,motivo", [
    ("umbral_reposicion", -1, "rango"), ("umbral_reposicion", 2.5, "entero"), ("umbral_reposicion", True, "entero"),
    ("costo_compra", -10, "rango"), ("costo_compra", "abc", "numero"), ("unidad_medida", "barril", "lista"),
    ("sku", "L*", "longitud"), ("sku", "LA*C", "formato"), ("categoria_id", 99, "no_existe"), ("nombre", "", "requerido"),
])
def test_producto_invalido_400(client_propietario, catalogo, campo, valor, motivo):
    r = client_propietario.post("/api/productos", json={**PRODUCTO, campo: valor})
    assert r.status_code == 400, r.get_json()
    assert r.get_json()["error"]["campos"] == {campo: motivo}


def test_listar_productos_con_forma_del_mock(client_trabajador, producto):
    cuerpo = client_trabajador.get("/api/productos").get_json()
    assert cuerpo["origen_datos"] == "SIMULADO"
    assert set(cuerpo["productos"][0]) == set(_mock("productos.json")["productos"][0])


def test_detalle_producto(client_trabajador, producto):
    _conteo(client_trabajador, producto, 5)
    assert _venta(client_trabajador, producto, 1, 1).status_code == 201
    cuerpo = client_trabajador.get(f"/api/productos/{producto}").get_json()
    _incluye_campos(cuerpo, _mock("producto_detalle.json"))
    assert cuerpo["ultimos_movimientos"][0]["tipo"] == "VENTA"
    assert cuerpo["ultimo_conteo"]["cantidad_contada"] == 5
    assert client_trabajador.get("/api/productos/999").status_code == 404


def test_catalogos(client_trabajador, catalogo):
    cuerpo = client_trabajador.get("/api/catalogos").get_json()
    assert cuerpo["categorias"] == [{"id": 1, "nombre": "Lacas"}]
    assert cuerpo["proveedores"][0]["plazo_entrega_dias"] == 3
    assert "medio_galon" in cuerpo["unidades_medida"]


# --- Conteos y saldo ---------------------------------------------------------------------

def test_conteo_de_5_y_venta_de_2_deja_saldo_3(client_trabajador, producto):
    conteo = _conteo(client_trabajador, producto, 5)
    _incluye_campos(conteo, _mock("conteo_creado.json"))
    assert conteo["producto"]["saldo_actual"] == 5
    r = _venta(client_trabajador, producto, 2, 2)
    assert r.status_code == 201
    venta = r.get_json()
    _incluye_campos(venta, {k: v for k, v in _mock("venta_creada.json").items() if k != "alerta"})
    assert (venta["producto"]["saldo_anterior"], venta["producto"]["saldo_actual"]) == (5, 3)
    assert venta["no_atendida"] == 0 and venta["alerta"] is None


def test_conteo_cantidad_invalida_400(client_trabajador, producto):
    r = client_trabajador.post("/api/conteos", json={"producto_id": producto, "cantidad_contada": -1, "origen_ref": _ref()})
    assert r.status_code == 400 and r.get_json()["error"]["campos"] == {"cantidad_contada": "rango"}


def test_conteo_de_producto_inexistente_404(client_trabajador, catalogo):
    r = client_trabajador.post("/api/conteos", json={"producto_id": 77, "cantidad_contada": 1, "origen_ref": _ref()})
    assert r.status_code == 404


# --- Ventas -------------------------------------------------------------------------------

def test_venta_mayor_que_el_saldo_409_y_no_guarda_nada(client_trabajador, producto, db):
    _conteo(client_trabajador, producto, 2)
    antes = (_contar(db, "movimientos"), _contar(db, "solicitudes_clientes"), _contar(db, "auditoria"))
    r = _venta(client_trabajador, producto, 3, 3)
    assert r.status_code == 409
    assert r.get_json() == {"error": {"codigo": "STOCK_INSUFICIENTE",
                                      "mensaje": "Saldo disponible: 2. No se puede entregar 3.",
                                      "campos": {"cantidad_entregada": "supera_saldo"}}}
    assert (_contar(db, "movimientos"), _contar(db, "solicitudes_clientes"), _contar(db, "auditoria")) == antes


def test_entregada_mayor_que_solicitada_400(client_trabajador, producto):
    _conteo(client_trabajador, producto, 9)
    r = _venta(client_trabajador, producto, 2, 3)
    assert r.status_code == 400
    assert r.get_json() == _mock("error_400_validacion.json")


def test_venta_sin_conteo(client_trabajador, producto):
    r = _venta(client_trabajador, producto, 2, 1)
    assert r.status_code == 409 and r.get_json()["error"]["codigo"] == "SIN_CONTEO"
    # Sin entregar nada sí se registra: la demanda no atendida cuenta aunque no haya conteo
    r = _venta(client_trabajador, producto, 2, 0)
    assert r.status_code == 201
    assert (r.get_json()["movimiento_id"], r.get_json()["no_atendida"]) == (None, 2)


def test_venta_reenviada_no_se_duplica(client_trabajador, producto, db):
    _conteo(client_trabajador, producto, 5)
    cuerpo = {"producto_id": producto, "cantidad_solicitada": 1, "cantidad_entregada": 1, "origen_ref": "folio-0042"}
    assert client_trabajador.post("/api/ventas", json=cuerpo).status_code == 201
    r = client_trabajador.post("/api/ventas", json=cuerpo)
    assert r.status_code == 200 and r.get_json()["duplicado"] is True
    assert _contar(db, "movimientos") == 1 and _contar(db, "solicitudes_clientes") == 1


def test_cada_operacion_deja_auditoria(client_propietario, producto, db):
    _conteo(client_propietario, producto, 5)
    _venta(client_propietario, producto, 1, 1)
    _venta(client_propietario, producto, 1, 0)
    client_propietario.post("/api/movimientos", json={"tipo": "ENTRADA", "producto_id": producto, "cantidad": 3,
                                                      "origen_ref": _ref()})
    acciones = list(db.session.execute(text(
        "SELECT accion FROM auditoria WHERE accion <> 'LOGIN_OK' ORDER BY id")).scalars())
    assert acciones == ["PRODUCTO_CREADO", "CONTEO_REGISTRADO", "VENTA_REGISTRADA", "ATENCION_SIN_ENTREGA",
                        "ENTRADA_REGISTRADA"]


# --- Cliente que regresa --------------------------------------------------------------------

def test_cliente_que_regresa(client_trabajador, client_propietario, producto, db):
    _conteo(client_trabajador, producto, 1)
    original = _venta(client_trabajador, producto, 3, 1).get_json()            # faltaron 2
    client_trabajador.post("/api/movimientos", json={"tipo": "ENTRADA", "producto_id": producto, "cantidad": 10,
                                                     "origen_ref": _ref()})
    pendientes = client_trabajador.get(f"/api/productos/{producto}").get_json()["faltantes_pendientes"]
    assert pendientes[0]["solicitud_id"] == original["solicitud_id"] and pendientes[0]["faltante_pendiente"] == 2

    r = _venta(client_trabajador, producto, 3, 3, solicitud_previa_id=original["solicitud_id"])
    assert r.status_code == 400 and r.get_json()["error"]["campos"] == {"cantidad_solicitada": "supera_faltante"}
    r = _venta(client_trabajador, producto, 2, 2, solicitud_previa_id=original["solicitud_id"])
    assert r.status_code == 201
    regreso = r.get_json()
    assert regreso["solicitud_previa_id"] == original["solicitud_id"]
    r = _venta(client_trabajador, producto, 1, 1, solicitud_previa_id=regreso["solicitud_id"])
    assert r.status_code == 400 and r.get_json()["error"]["campos"] == {"solicitud_previa_id": "no_es_original"}

    m = db.session.execute(text(
        f"SELECT * FROM fn_metricas_periodo(CURRENT_DATE) WHERE producto_id = {producto}")).mappings().one()
    assert (m["vendidas_30d"], m["demanda_30d"], m["no_atendidas_30d"]) == (3, 3, 2)
    assert client_trabajador.get(f"/api/productos/{producto}").get_json()["faltantes_pendientes"] == []


# --- Entradas y ajustes -----------------------------------------------------------------------

def test_entrada_del_trabajador(client_trabajador, producto):
    _conteo(client_trabajador, producto, 0)
    r = client_trabajador.post("/api/movimientos", json={"tipo": "ENTRADA", "producto_id": producto, "cantidad": 24,
                                                         "origen_ref": _ref()})
    assert r.status_code == 201
    cuerpo = r.get_json()
    _incluye_campos(cuerpo, _mock("movimiento_creado.json"))
    assert (cuerpo["producto"]["saldo_anterior"], cuerpo["producto"]["saldo_actual"]) == (0, 24)


def test_trabajador_no_puede_ajustar_403(client_trabajador, producto):
    _conteo(client_trabajador, producto, 5)
    r = client_trabajador.post("/api/movimientos", json={"tipo": "AJUSTE", "producto_id": producto, "cantidad": -1,
                                                         "justificacion": "Galón dañado en bodega", "origen_ref": _ref()})
    assert r.status_code == 403 and r.get_json()["error"]["codigo"] == "SIN_PERMISO"


def test_ajuste_sin_justificacion_400(client_propietario, producto):
    _conteo(client_propietario, producto, 5)
    for just in (None, "corto"):
        r = client_propietario.post("/api/movimientos", json={"tipo": "AJUSTE", "producto_id": producto,
                                                              "cantidad": -1, "justificacion": just, "origen_ref": _ref()})
        assert r.status_code == 400 and "justificacion" in r.get_json()["error"]["campos"]


def test_ajuste_del_propietario_y_saldo_negativo_409(client_propietario, producto):
    _conteo(client_propietario, producto, 5)
    base = {"tipo": "AJUSTE", "producto_id": producto, "justificacion": "Galones dañados en bodega"}
    r = client_propietario.post("/api/movimientos", json={**base, "cantidad": -2, "origen_ref": _ref()})
    assert r.status_code == 201 and r.get_json()["producto"]["saldo_actual"] == 3
    r = client_propietario.post("/api/movimientos", json={**base, "cantidad": -4, "origen_ref": _ref()})
    assert r.status_code == 409 and r.get_json()["error"]["codigo"] == "STOCK_INSUFICIENTE"
    r = client_propietario.post("/api/movimientos", json={**base, "cantidad": 0, "origen_ref": _ref()})
    assert r.status_code == 400


def test_entrada_sin_conteo_409(client_trabajador, producto):
    r = client_trabajador.post("/api/movimientos", json={"tipo": "ENTRADA", "producto_id": producto, "cantidad": 3,
                                                         "origen_ref": _ref()})
    assert r.status_code == 409 and r.get_json()["error"]["codigo"] == "SIN_CONTEO"


def test_origen_ref_de_otro_tipo_de_registro_409(client_trabajador, producto):
    _conteo(client_trabajador, producto, 5)
    assert client_trabajador.post("/api/movimientos", json={"tipo": "ENTRADA", "producto_id": producto,
                                                            "cantidad": 1, "origen_ref": "folio-7"}).status_code == 201
    r = client_trabajador.post("/api/ventas", json={"producto_id": producto, "cantidad_solicitada": 1,
                                                    "cantidad_entregada": 1, "origen_ref": "folio-7"})
    assert r.status_code == 409 and r.get_json()["error"]["codigo"] == "ORIGEN_REF_EN_USO"
