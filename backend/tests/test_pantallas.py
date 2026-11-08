"""Pantallas integradas: cargan la lógica compartida y respetan la sesión y el rol."""

import pytest


@pytest.mark.parametrize("ruta", ["/dashboard", "/registro"])
def test_sin_sesion_redirige_al_login(client, ruta):
    r = client.get(ruta)
    assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_dashboard_carga_la_logica_compartida(client_trabajador):
    html = client_trabajador.get("/dashboard").get_data(as_text=True)
    for fragmento in ('id="kpis"', 'id="tabla-criticos"', 'id="tabla-inventario"', 'id="subtitulo"',
                      'id="etiqueta-simulado"', "js/api.js", "js/comun.js", "js/dashboard.js"):
        assert fragmento in html, fragmento
    assert 'name="csrf-token"' in html  # api.js usa la API real, no los mocks


def test_registro_del_trabajador_sin_crear_producto(client_trabajador):
    html = client_trabajador.get("/registro").get_data(as_text=True)
    assert 'id="form-venta"' in html and 'id="form-conteo"' in html and 'id="form-movimiento"' in html
    assert 'id="form-producto"' not in html
    assert 'data-rol="trabajador"' in html


def test_registro_del_propietario_con_crear_producto(client_propietario):
    html = client_propietario.get("/registro").get_data(as_text=True)
    assert 'id="form-producto"' in html and 'data-rol="propietario"' in html


@pytest.mark.parametrize("archivo", ["api.js", "comun.js", "dashboard.js", "registro.js"])
def test_archivos_js_se_sirven(client, archivo):
    r = client.get(f"/static/js/{archivo}")
    assert r.status_code == 200 and len(r.data) > 500


def test_planificacion_del_propietario(client_propietario):
    html = client_propietario.get("/planificacion").get_data(as_text=True)
    for fragmento in ('id="tabla-sugeridos"', 'id="guardar-borrador"', 'id="tabla-pedidos"', "js/planificacion.js"):
        assert fragmento in html, fragmento


def test_planificacion_del_trabajador_sin_sugeridos(client_trabajador):
    html = client_trabajador.get("/planificacion").get_data(as_text=True)
    assert 'id="tabla-sugeridos"' not in html and 'id="tabla-pedidos"' in html


@pytest.mark.parametrize("pantalla", ["dashboard", "registro", "planificacion"])
def test_prototipo_usa_la_misma_logica(pantalla):
    """El prototipo del Rol 4 carga los mismos archivos JS que Flask: no hay una segunda copia."""
    from pathlib import Path
    html = (Path(__file__).resolve().parents[2] / "frontend" / "prototipo" / f"{pantalla}.html").read_text()
    assert f'src="../static/js/{pantalla}.js"' in html and 'src="../static/js/comun.js"' in html
    assert "function " not in html.split("<script>window.USE_MOCK")[1].split(f"{pantalla}.js")[0].replace(
        'addEventListener("change", () =>', "")
