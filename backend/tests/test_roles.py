def test_api_sin_sesion_responde_401_json(client):
    r = client.get("/api/auditoria")
    assert r.status_code == 401
    assert r.get_json() == {"error": {"codigo": "NO_AUTENTICADO", "mensaje": "Debes iniciar sesión.", "campos": {}}}


def test_trabajador_no_ve_auditoria_403(client_trabajador):
    r = client_trabajador.get("/api/auditoria")
    assert r.status_code == 403
    err = r.get_json()["error"]
    assert err["codigo"] == "SIN_PERMISO"
    assert "propietario" in err["mensaje"]


def test_propietario_consulta_auditoria(client_propietario):
    r = client_propietario.get("/api/auditoria")
    assert r.status_code == 200
    registros = r.get_json()["registros"]
    assert registros[0]["accion"] == "LOGIN_OK"
    assert registros[0]["usuario"] == "propietario"


def test_auditoria_limite_invalido_400(client_propietario):
    r = client_propietario.get("/api/auditoria?limite=abc")
    assert r.status_code == 400
    assert r.get_json()["error"]["campos"] == {"limite": "entero"}
    assert client_propietario.get("/api/auditoria?limite=999").status_code == 400
