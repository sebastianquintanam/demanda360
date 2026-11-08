"""Fixtures de prueba.

Las pruebas corren contra un PostgreSQL real (base demanda360_test) porque lo que
más importa probar vive en la base: CHECK, UNIQUE, triggers y bloqueos.
La base de prueba se crea sola y se recarga desde database/sql/*.sql en cada corrida.

Variables:
  TEST_DATABASE_URL  (opcional) p. ej. postgresql+psycopg://user:clave@localhost:5432/demanda360_test
                     Si no existe, se usa el .env con la base "demanda360_test".
"""

from pathlib import Path

import psycopg
import pytest
from sqlalchemy.engine import make_url

from app import create_app
from app.config import TestConfig
from app.extensions import db as _db
from app.models import Usuario

RAIZ = Path(__file__).resolve().parents[2]
SQL_DIR = RAIZ / "database" / "sql"
TABLAS = (
    "pedido_detalles", "pedidos", "alertas_enviadas", "auditoria", "solicitudes_clientes",
    "movimientos", "conteos_fisicos", "productos", "proveedores", "categorias", "usuarios",
)
CLAVE_PROPIETARIO = "clave-propietario-123"
CLAVE_TRABAJADOR = "clave-trabajador-123"


def _conninfo(url) -> str:
    # Ojo: str(URL) oculta la contraseña; por eso se renderiza explícitamente
    return make_url(url).set(drivername="postgresql").render_as_string(hide_password=False)


def _preparar_base(url: str) -> None:
    destino = make_url(url)
    nombre = destino.database
    admin = _conninfo(destino.set(database="postgres"))
    with psycopg.connect(admin, autocommit=True) as conn:
        existe = conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (nombre,)).fetchone()
        if not existe:
            conn.execute(f'CREATE DATABASE "{nombre}"')
    with psycopg.connect(_conninfo(url), autocommit=True) as conn:
        conn.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        for archivo in sorted(SQL_DIR.glob("*.sql")):
            conn.execute(archivo.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def app():
    _preparar_base(TestConfig.SQLALCHEMY_DATABASE_URI)
    aplicacion = create_app(TestConfig)
    yield aplicacion


@pytest.fixture(autouse=True)
def base_limpia(app):
    with app.app_context():
        _db.session.execute(_db.text(f"TRUNCATE {', '.join(TABLAS)} RESTART IDENTITY CASCADE"))
        _db.session.commit()
    yield
    with app.app_context():
        _db.session.rollback()
        _db.session.remove()


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db


@pytest.fixture
def usuarios(app):
    with app.app_context():
        for usuario, rol, clave in (
            ("propietario", "propietario", CLAVE_PROPIETARIO),
            ("trabajador", "trabajador", CLAVE_TRABAJADOR),
        ):
            u = Usuario(usuario=usuario, nombre=f"{usuario.title()} prueba", rol=rol)
            u.set_password(clave)
            _db.session.add(u)
        _db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


def _login(app, usuario, clave):
    c = app.test_client()
    r = c.post("/login", data={"usuario": usuario, "clave": clave})
    assert r.status_code == 302, r.get_data(as_text=True)
    return c


@pytest.fixture
def client_propietario(app, usuarios):
    return _login(app, "propietario", CLAVE_PROPIETARIO)


@pytest.fixture
def client_trabajador(app, usuarios):
    return _login(app, "trabajador", CLAVE_TRABAJADOR)
