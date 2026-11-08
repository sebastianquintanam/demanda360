"""Comandos de administración: `flask <comando>` (dentro del contenedor: `docker compose exec web flask <comando>`)."""

import click
from flask import Flask

from .extensions import db
from .models import Usuario
from .security import ROL_PROPIETARIO, ROL_TRABAJADOR
from .services import auditoria

USUARIOS_DEMO = (
    ("propietario", "Propietario (demo)", ROL_PROPIETARIO, "DEMO_PASSWORD_PROPIETARIO"),
    ("trabajador", "Trabajador (demo)", ROL_TRABAJADOR, "DEMO_PASSWORD_TRABAJADOR"),
)
LONGITUD_MINIMA = 10


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
