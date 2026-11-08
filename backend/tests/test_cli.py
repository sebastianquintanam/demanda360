from app.models import Usuario


def test_crear_usuarios_demo_idempotente(app, db, monkeypatch):
    monkeypatch.setenv("DEMO_PASSWORD_PROPIETARIO", "clave-larga-propietario")
    monkeypatch.setenv("DEMO_PASSWORD_TRABAJADOR", "clave-larga-trabajador")
    runner = app.test_cli_runner()
    r1 = runner.invoke(args=["crear-usuarios-demo"])
    assert r1.exit_code == 0, r1.output
    r2 = runner.invoke(args=["crear-usuarios-demo"])
    assert "ya existe" in r2.output
    roles = {u.usuario: u.rol for u in db.session.execute(db.select(Usuario)).scalars()}
    assert roles == {"propietario": "propietario", "trabajador": "trabajador"}


def test_crear_usuarios_demo_rechaza_clave_corta(app, monkeypatch):
    monkeypatch.setenv("DEMO_PASSWORD_PROPIETARIO", "corta")
    monkeypatch.setenv("DEMO_PASSWORD_TRABAJADOR", "corta")
    r = app.test_cli_runner().invoke(args=["crear-usuarios-demo"])
    assert r.exit_code != 0
