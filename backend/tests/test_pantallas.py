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
