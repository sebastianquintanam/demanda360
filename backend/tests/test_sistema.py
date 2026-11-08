def test_health_ok(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.get_json() == {"estado": "ok", "bd": "ok"}


def test_cabeceras_de_seguridad_y_request_id(client):
    r = client.get("/api/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert r.headers["Cache-Control"] == "no-store"
    assert len(r.headers["X-Request-ID"]) > 0


def test_ruta_api_inexistente_responde_404_con_formato(client):
    r = client.get("/api/no-existe")
    assert r.status_code == 404
    assert r.get_json()["error"]["codigo"] == "NO_ENCONTRADO"


def test_metodo_no_permitido_responde_json(client):
    r = client.delete("/api/health")
    assert r.status_code == 405
    assert r.get_json()["error"]["codigo"] == "METODO_NO_PERMITIDO"
