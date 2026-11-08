from app.models import Auditoria, Usuario
from tests.conftest import CLAVE_PROPIETARIO


def test_pagina_protegida_sin_sesion_redirige_al_login(client):
    r = client.get("/dashboard")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_login_correcto_redirige_y_audita(client, usuarios, db):
    r = client.post("/login", data={"usuario": "PROPIETARIO ", "clave": CLAVE_PROPIETARIO})
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/dashboard")
    acciones = [a.accion for a in db.session.execute(db.select(Auditoria)).scalars()]
    assert "LOGIN_OK" in acciones


def test_login_fallido_mensaje_generico_y_auditado(client, usuarios, db):
    r1 = client.post("/login", data={"usuario": "propietario", "clave": "incorrecta-123"})
    r2 = client.post("/login", data={"usuario": "no-existe", "clave": "incorrecta-123"})
    assert r1.status_code == r2.status_code == 401
    texto = "Usuario o contraseña incorrectos."
    assert texto in r1.get_data(as_text=True) and texto in r2.get_data(as_text=True)
    filas = db.session.execute(db.select(Auditoria).filter_by(accion="LOGIN_FALLIDO")).scalars().all()
    assert len(filas) == 2
    assert all("clave" not in f.detalle and "password" not in f.detalle for f in filas)


def test_usuario_inactivo_no_entra(client, usuarios, db):
    u = db.session.execute(db.select(Usuario).filter_by(usuario="propietario")).scalar_one()
    u.activo = False
    db.session.commit()
    r = client.post("/login", data={"usuario": "propietario", "clave": CLAVE_PROPIETARIO})
    assert r.status_code == 401


def test_redireccion_externa_bloqueada(client, usuarios):
    r = client.post("/login?next=https://sitio-malicioso.example/", data={"usuario": "propietario", "clave": CLAVE_PROPIETARIO})
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/dashboard")


def test_redireccion_interna_permitida(client, usuarios):
    r = client.post("/login?next=/registro", data={"usuario": "propietario", "clave": CLAVE_PROPIETARIO})
    assert r.headers["Location"].endswith("/registro")


def test_logout_solo_por_post(client_propietario):
    assert client_propietario.get("/logout").status_code == 405
    r = client_propietario.post("/logout")
    assert r.status_code == 302
    assert client_propietario.get("/dashboard").status_code == 302  # ya sin sesión


def test_contrasena_guardada_como_hash(usuarios, db):
    u = db.session.execute(db.select(Usuario).filter_by(usuario="propietario")).scalar_one()
    assert u.password_hash != CLAVE_PROPIETARIO
    assert u.password_hash.startswith(("scrypt:", "pbkdf2:"))


def test_csrf_activo_rechaza_formulario_sin_token(app, usuarios):
    app.config["WTF_CSRF_ENABLED"] = True
    try:
        c = app.test_client()
        r = c.post("/login", data={"usuario": "propietario", "clave": CLAVE_PROPIETARIO})
        assert r.status_code == 302 and "error=sesion" in r.headers["Location"]
        assert c.get("/dashboard").status_code == 302  # no inició sesión
    finally:
        app.config["WTF_CSRF_ENABLED"] = False


def test_csrf_activo_acepta_formulario_con_token(app, usuarios):
    app.config["WTF_CSRF_ENABLED"] = True
    try:
        c = app.test_client()
        html = c.get("/login").get_data(as_text=True)
        token = html.split('name="csrf_token" type="hidden" value="')[1].split('"')[0]
        r = c.post("/login", data={"usuario": "propietario", "clave": CLAVE_PROPIETARIO, "csrf_token": token})
        assert r.status_code == 302 and r.headers["Location"].endswith("/dashboard")
    finally:
        app.config["WTF_CSRF_ENABLED"] = False
