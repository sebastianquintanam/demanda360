"""Comandos de administración: `flask <comando>` (dentro del contenedor: `docker compose exec web flask <comando>`)."""

from pathlib import Path

import click
import psycopg
from flask import Flask, current_app
from sqlalchemy.engine import make_url

from .extensions import db
from .models import Usuario
from .security import ROL_PROPIETARIO, ROL_TRABAJADOR
from .services import auditoria

USUARIOS_DEMO = (
    ("propietario", "Propietario (demo)", ROL_PROPIETARIO, "DEMO_PASSWORD_PROPIETARIO"),
    ("trabajador", "Trabajador (demo)", ROL_TRABAJADOR, "DEMO_PASSWORD_TRABAJADOR"),
)
LONGITUD_MINIMA = 10

RAIZ = Path(__file__).resolve().parents[2]
SQL_VISTAS = RAIZ / "database" / "sql" / "02_vistas.sql"
SQL_DEMO = RAIZ / "database" / "seeds" / "10_demo.sql"


def _ejecutar_sql(archivo: Path) -> None:
    """Corre un archivo .sql completo con psycopg (sin parámetros: los % y : del texto no se interpretan).

    Los archivos traen su propio BEGIN/COMMIT o son idempotentes; si algo falla,
    PostgreSQL deshace la transacción y aquí se muestra el mensaje sin trazas.
    """
    if not archivo.exists():
        raise click.ClickException(f"No se encontró {archivo}.")
    url = make_url(current_app.config["SQLALCHEMY_DATABASE_URI"]).set(drivername="postgresql")
    try:
        with psycopg.connect(url.render_as_string(hide_password=False), autocommit=True) as conn:
            conn.execute(archivo.read_text(encoding="utf-8"))
    except psycopg.Error as e:
        mensaje = (e.diag.message_primary if getattr(e, "diag", None) else None) or str(e).splitlines()[0]
        raise click.ClickException(f"{archivo.name}: {mensaje}") from None


def _validar_clave(clave: str) -> str:
    if len(clave) < LONGITUD_MINIMA:
        raise click.BadParameter(f"La contraseña debe tener al menos {LONGITUD_MINIMA} caracteres.")
    return clave


def registrar_comandos(app: Flask) -> None:
    @app.cli.command("crear-usuarios-demo")
    @click.option("--reemplazar-claves", is_flag=True, help="Cambia la contraseña si el usuario ya existe.")
    def crear_usuarios_demo(reemplazar_claves: bool) -> None:
        """Crea los usuarios 'propietario' y 'trabajador'.

        La contraseña se toma de DEMO_PASSWORD_PROPIETARIO / DEMO_PASSWORD_TRABAJADOR
        (en .env) o se pide por teclado sin mostrarla. Nunca queda escrita en el repositorio.
        """
        import os

        for usuario, nombre, rol, variable in USUARIOS_DEMO:
            existente = db.session.execute(db.select(Usuario).filter_by(usuario=usuario)).scalar_one_or_none()
            if existente and not reemplazar_claves:
                click.echo(f"· '{usuario}' ya existe (rol {existente.rol}); no se cambia.")
                continue

            clave = os.environ.get(variable) or click.prompt(
                f"Contraseña para '{usuario}'", hide_input=True, confirmation_prompt=True
            )
            _validar_clave(clave)

            if existente:
                existente.set_password(clave)
                auditoria.registrar("CLAVE_REEMPLAZADA", "usuarios", existente.id, usuario_id=existente.id)
                click.echo(f"✓ Contraseña de '{usuario}' reemplazada.")
            else:
                nuevo = Usuario(usuario=usuario, nombre=nombre, rol=rol)
                nuevo.set_password(clave)
                db.session.add(nuevo)
                db.session.flush()
                auditoria.registrar("USUARIO_CREADO", "usuarios", nuevo.id,
                                    detalle={"rol": rol, "origen": "cli"}, usuario_id=nuevo.id)
                click.echo(f"✓ Usuario '{usuario}' creado con rol {rol}.")
        db.session.commit()

    @app.cli.command("aplicar-vistas")
    def aplicar_vistas() -> None:
        """(Re)crea las funciones y vistas de database/sql/02_vistas.sql. No borra datos."""
        _ejecutar_sql(SQL_VISTAS)
        click.echo("✓ Vistas y funciones de KPI actualizadas.")

    @app.cli.command("cargar-demo")
    def cargar_demo() -> None:
        """Carga los datos SIMULADOS de septiembre (database/seeds/10_demo.sql).

        Solo funciona en una base sin productos y con los usuarios demo creados.
        Antes actualiza las vistas, y al final muestra los KPI del 30 de septiembre.
        """
        _ejecutar_sql(SQL_VISTAS)
        _ejecutar_sql(SQL_DEMO)
        filas = db.session.execute(db.text(
            "SELECT codigo, nombre, valor, unidad, detalle FROM fn_kpi_resumen(DATE '2026-09-30')"
        )).all()
        click.echo("✓ Datos demo cargados (SIMULADOS, 1–30 sep 2026). KPI al 30 de septiembre:")
        for codigo, nombre, valor, unidad, detalle in filas:
            click.echo(f"  {codigo} {nombre}: {valor} {unidad} · {detalle}")
