"""Etapa 2: datos demo, saldo, estados y KPI.

Las cifras esperadas salen de los mocks del frontend (que tienen las del Figma):
si el SQL y los mocks dejan de coincidir, esta prueba lo dice antes que la demo.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest
from sqlalchemy import text

RAIZ = Path(__file__).resolve().parents[2]
MOCKS = RAIZ / "frontend" / "static" / "mock"
CORTE = "DATE '2026-09-30'"
LIMITE = "fn_limite_corte(DATE '2026-09-30')"


def _mock(nombre):
    return json.loads((MOCKS / nombre).read_text(encoding="utf-8"))


def _filas(db, sql):
    return [dict(r._mapping) for r in db.session.execute(text(sql))]


@pytest.fixture
def demo(app, db, usuarios):
    resultado = app.test_cli_runner().invoke(args=["cargar-demo"])
    assert resultado.exit_code == 0, resultado.output
    return resultado.output


# --- Datos demo = cifras del Figma ------------------------------------------------

def test_kpi_1_a_3_cuadran_con_el_figma(db, demo):
    kpis = {k["codigo"]: k for k in _filas(db, f"SELECT * FROM fn_kpi_resumen({CORTE})")}
    for esperado in _mock("dashboard.json")["kpis"]:
        k = kpis[esperado["codigo"]]
        assert float(k["valor"]) == esperado["valor"], k
        assert (int(k["numerador"]), k["denominador"]) == (esperado["numerador"], esperado["denominador"])
        assert k["origen_datos"] == "SIMULADO"
    assert "27.3" in demo and "8.6" in demo and "50.0" in demo


def test_kpi_4_y_5_con_pedidos_demo(db, demo):
    kpis = {k["codigo"]: k for k in _filas(db, "SELECT * FROM vw_kpi_resumen")}
    # (3 + 6 + 5) h / 3 pedidos con respuesta; el cancelado y el enviado sin respuesta no se promedian
    assert float(kpis["KPI4"]["valor"]) == 4.7
    assert kpis["KPI4"]["denominador"] == 3
    assert "2 enviado(s) sin respuesta" in kpis["KPI4"]["detalle"]
    # 2 de 3 confirmados en el primer intento (el tercero es un reintento con otro proveedor)
    assert float(kpis["KPI5"]["valor"]) == 66.7
    assert kpis["KPI5"]["mejor_si"] == "mayor"


def test_totales_del_mes(db, demo):
    t = _filas(db, """
        SELECT sum(vendidas) AS vendidas, sum(solicitadas) AS solicitadas, sum(no_atendidas) AS no_atendidas,
               count(DISTINCT fecha) AS dias
        FROM vw_ventas_diarias""")[0]
    assert (t["vendidas"], t["solicitadas"], t["no_atendidas"], t["dias"]) == (127, 139, 12, 30)


def test_estado_y_rotacion_por_producto_igual_al_mock(db, demo):
    reales = {r["sku"]: r for r in _filas(db, "SELECT * FROM vw_inventario_actual")}
    esperados = _mock("rotacion.json")["productos"]
    assert len(reales) == len(esperados) == 11
    for e in esperados:
        r = reales[e["sku"]]
        assert r["producto_id"] == e["id"], e["sku"]
        assert r["plazo_entrega_dias"] == e["plazo_entrega_dias"], e["sku"]
        for campo in ("saldo", "estado", "vendidas_30d", "no_atendidas_30d", "dias_con_registro", "cobertura_dias"):
            assert r[campo] == e[campo], (e["sku"], campo, r[campo], e[campo])
        dd = None if r["demanda_diaria"] is None else float(r["demanda_diaria"])
        assert dd == e["demanda_diaria"], (e["sku"], dd)


def test_umbral_y_proveedor_igual_al_mock(db, demo):
    reales = {r["sku"]: r for r in _filas(db, "SELECT * FROM vw_inventario_actual")}
    for e in _mock("productos.json")["productos"]:
        r = reales[e["sku"]]
        assert (r["umbral_reposicion"], r["proveedor"], r["categoria"]) == (
            e["umbral_reposicion"], e["proveedor"], e["categoria"]), e["sku"]


def test_sugeridos_igual_al_mock(db, demo):
    mock = _mock("sugeridos.json")
    reales = {r["sku"]: r for r in _filas(db, "SELECT * FROM vw_sugeridos")}
    for e in mock["productos"]:
        r = reales[e["sku"]]
        assert r["sugerido"] == e["sugerido"], e["sku"]
        assert r["formula"] == e["formula"], (e["sku"], r["formula"])
    assert sum(r["sugerido"] or 0 for r in reales.values()) == mock["total_sugerido"] == 54
    assert reales["LAC-BP-01"]["sugerido"] == 24


def test_estado_actual_sin_ventas_nuevas_igual_al_corte(db, demo):
    actual = {r["sku"]: (r["saldo"], r["estado"]) for r in _filas(db, "SELECT * FROM vw_estado_productos")}
    corte = {r["sku"]: (r["saldo"], r["estado"]) for r in _filas(db, "SELECT * FROM vw_inventario_actual")}
    assert actual == corte


def test_cargar_demo_dos_veces_no_duplica(app, db, demo):
    antes = _filas(db, "SELECT count(*) AS n FROM movimientos")[0]["n"]
    resultado = app.test_cli_runner().invoke(args=["cargar-demo"])
    assert resultado.exit_code != 0
    assert "base vacía" in resultado.output
    db.session.rollback()
    assert _filas(db, "SELECT count(*) AS n FROM movimientos")[0]["n"] == antes


def test_cargar_demo_sin_usuarios_falla_sin_cargar_nada(app, db):
    resultado = app.test_cli_runner().invoke(args=["cargar-demo"])
    assert resultado.exit_code != 0
    assert "crear-usuarios-demo" in resultado.output
    assert _filas(db, "SELECT count(*) AS n FROM productos")[0]["n"] == 0


def test_archivo_demo_al_dia_con_el_generador():
    spec = importlib.util.spec_from_file_location("generar_demo", RAIZ / "database" / "seeds" / "generar_demo.py")
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = modulo  # lo exige @dataclass
    spec.loader.exec_module(modulo)
    assert modulo.SALIDA.read_text(encoding="utf-8") == modulo.generar(), \
        "10_demo.sql está desactualizado: corre python3 database/seeds/generar_demo.py"


# --- Reglas de cálculo con datos mínimos -------------------------------------------

@pytest.fixture
def catalogo(db, usuarios):
    db.session.execute(text("""
        INSERT INTO categorias (nombre) VALUES ('Lacas');
        INSERT INTO proveedores (codigo, nombre, plazo_entrega_dias) VALUES ('PRV-1', 'Proveedor (ficticio)', 3);
        INSERT INTO productos (sku, nombre, categoria_id, proveedor_id, presentacion, unidad_medida,
                               costo_compra, precio_venta, umbral_reposicion)
        VALUES ('PRB-01', 'Prueba 1', 1, 1, 'Galón', 'galon', 1, 1, 2),
               ('PRB-02', 'Prueba 2', 1, 1, 'Galón', 'galon', 1, 1, 2);
    """))
    db.session.commit()


def _sql(db, sql):
    db.session.execute(text(sql))
    db.session.commit()


def _conteo(db, producto, cantidad, fecha, ref):
    _sql(db, f"INSERT INTO conteos_fisicos (producto_id, cantidad_contada, fecha_hora, usuario_id, origen_ref)"
             f" VALUES ({producto}, {cantidad}, '{fecha}', 1, '{ref}')")


def _mov(db, producto, tipo, cantidad, fecha, ref, justificacion="NULL"):
    _sql(db, f"INSERT INTO movimientos (producto_id, tipo, cantidad, fecha_hora, usuario_id, origen_ref, justificacion)"
             f" VALUES ({producto}, '{tipo}', {cantidad}, '{fecha}', 1, '{ref}', {justificacion})")


def _venta(db, producto, solicitada, entregada, fecha, ref, previa="NULL"):
    mov = "NULL"
    if entregada:
        _mov(db, producto, "VENTA", entregada, fecha, ref + "-v")
        mov = f"(SELECT id FROM movimientos WHERE origen_ref = '{ref}-v')"
    _sql(db, "INSERT INTO solicitudes_clientes (producto_id, cantidad_solicitada, cantidad_entregada, fecha_hora,"
             f" usuario_id, movimiento_id, solicitud_previa_id, origen_ref)"
             f" VALUES ({producto}, {solicitada}, {entregada}, '{fecha}', 1, {mov}, {previa}, '{ref}')")


def _saldo(db, producto, hasta="'infinity'"):
    return _filas(db, f"SELECT saldo FROM fn_saldos({hasta}) WHERE producto_id = {producto}")[0]["saldo"]


def test_sin_conteo_el_saldo_es_nulo_no_cero(db, catalogo):
    _mov(db, 1, "ENTRADA", 5, "2026-09-02 10:00-05", "e1")
    assert _saldo(db, 1) is None
    estado = _filas(db, f"SELECT estado FROM fn_estado_productos({CORTE}, 'infinity') WHERE producto_id = 1")[0]
    assert estado["estado"] == "SIN_CONTEO"


def test_conteo_de_5_y_venta_de_2_deja_3(db, catalogo):
    _conteo(db, 1, 5, "2026-09-01 07:00-05", "c1")
    _venta(db, 1, 2, 2, "2026-09-02 10:00-05", "a1")
    assert _saldo(db, 1) == 3


def test_saldo_parte_del_ultimo_conteo_y_suma_movimientos_posteriores(db, catalogo):
    _conteo(db, 1, 10, "2026-09-01 07:00-05", "c1")
    _mov(db, 1, "VENTA", 4, "2026-09-02 10:00-05", "v1")           # antes del 2.º conteo: ya incluida en él
    _conteo(db, 1, 7, "2026-09-03 07:00-05", "c2")                 # el conteo manda (diferencia de 1)
    _mov(db, 1, "ENTRADA", 6, "2026-09-04 09:00-05", "e1")
    _mov(db, 1, "AJUSTE", -2, "2026-09-05 09:00-05", "a1", "'Dos galones dañados en bodega'")
    _mov(db, 1, "VENTA", 1, "2026-09-06 09:00-05", "v2")
    assert _saldo(db, 1) == 7 + 6 - 2 - 1


def test_saldo_al_corte_ignora_lo_posterior(db, catalogo):
    _conteo(db, 1, 5, "2026-09-01 07:00-05", "c1")
    _venta(db, 1, 1, 1, "2026-09-30 23:59:59.900-05", "a1")       # último instante del corte: cuenta
    _venta(db, 1, 1, 1, "2026-10-01 00:00-05", "a2")               # primer instante después: no cuenta
    assert _saldo(db, 1, LIMITE) == 4
    assert _saldo(db, 1) == 3
    m = _filas(db, f"SELECT vendidas_30d FROM fn_metricas_periodo({CORTE}) WHERE producto_id = 1")[0]
    assert m["vendidas_30d"] == 1


def test_orden_de_estados(db, catalogo):
    # Producto 1: saldo igual al umbral → CRÍTICO aunque tenga menos de 30 días
    _conteo(db, 1, 2, "2026-09-20 07:00-05", "c1")
    # Producto 2: 30 días completos (desde el 1 de septiembre) y 3 vendidas → NORMAL
    _conteo(db, 2, 20, "2026-09-01 07:00-05", "c2")
    _venta(db, 2, 3, 3, "2026-09-10 10:00-05", "a1")
    estados = {r["producto_id"]: r for r in _filas(db, f"SELECT * FROM fn_estado_productos({CORTE}, {LIMITE})")}
    assert estados[1]["estado"] == "CRITICO"
    assert estados[2]["estado"] == "NORMAL" and estados[2]["dias_con_registro"] == 30


def test_menos_de_30_dias_es_datos_insuficientes(db, catalogo):
    _conteo(db, 2, 20, "2026-09-02 07:00-05", "c2")                # 29 días al 30 de septiembre
    e = _filas(db, f"SELECT * FROM fn_estado_productos({CORTE}, {LIMITE}) WHERE producto_id = 2")[0]
    assert (e["dias_con_registro"], e["estado"], e["demanda_diaria"]) == (29, "DATOS_INSUFICIENTES", None)
    k3 = _filas(db, f"SELECT * FROM fn_kpi_resumen({CORTE}) WHERE codigo = 'KPI3'")[0]
    assert k3["denominador"] == 0 and k3["valor"] is None


def test_cliente_que_regresa_no_suma_demanda(db, catalogo):
    _conteo(db, 1, 1, "2026-09-01 07:00-05", "c1")
    _venta(db, 1, 3, 1, "2026-09-05 10:00-05", "a1")               # pidió 3, había 1: faltaron 2
    _mov(db, 1, "ENTRADA", 10, "2026-09-08 09:00-05", "e1")
    _venta(db, 1, 2, 2, "2026-09-09 10:00-05", "a2",                # vuelve por los 2 que faltaban
           previa="(SELECT id FROM solicitudes_clientes WHERE origen_ref = 'a1')")
    k2 = _filas(db, f"SELECT * FROM fn_kpi_resumen({CORTE}) WHERE codigo = 'KPI2'")[0]
    assert (int(k2["numerador"]), k2["denominador"]) == (2, 3)     # el faltante original se conserva
    m = _filas(db, f"SELECT * FROM fn_metricas_periodo({CORTE}) WHERE producto_id = 1")[0]
    assert (m["vendidas_30d"], m["demanda_30d"]) == (3, 3)         # vendió 3; la demanda real fue 3
    sol = {r["solicitud_id"]: r for r in _filas(db, "SELECT * FROM vw_solicitudes")}
    assert [r["cuenta_en_kpi2"] for r in sol.values()] == ["SI", "NO"]


def test_venta_de_hoy_cambia_el_saldo_pero_no_los_kpi_del_corte(db, demo):
    kpi_antes = _filas(db, "SELECT codigo, valor FROM vw_kpi_resumen")
    pid = _filas(db, "SELECT id FROM productos WHERE sku = 'SEL-CA-01'")[0]["id"]
    _venta(db, pid, 1, 1, "2026-11-08 10:00-05", "en-vivo")
    assert _filas(db, "SELECT codigo, valor FROM vw_kpi_resumen") == kpi_antes
    actual = _filas(db, f"SELECT saldo, estado FROM vw_estado_productos WHERE producto_id = {pid}")[0]
    assert (actual["saldo"], actual["estado"]) == (3, "CRITICO")
    # Un producto creado hoy no aparece en los CSV de septiembre
    _sql(db, """INSERT INTO productos (sku, nombre, categoria_id, proveedor_id, presentacion, unidad_medida,
                costo_compra, precio_venta, umbral_reposicion) VALUES ('NUE-01', 'Nuevo', 1, 1, 'Galón', 'galon', 1, 1, 1)""")
    assert len(_filas(db, "SELECT * FROM vw_inventario_actual")) == 11
    assert len(_filas(db, "SELECT * FROM vw_ventas_diarias")) == 330


def test_el_corte_se_cambia_por_sesion(db, demo):
    db.session.execute(text("SET LOCAL demanda360.corte = '2026-09-15'"))
    fila = _filas(db, "SELECT corte, periodo_desde FROM vw_kpi_resumen LIMIT 1")[0]
    assert str(fila["corte"]) == "2026-09-15" and str(fila["periodo_desde"]) == "2026-08-17"
    db.session.rollback()  # SET LOCAL termina con la transacción
