"""Login y logout con Flask-Login. El login es un formulario HTML (no una ruta /api)."""

import logging

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Length

from ..extensions import db
from ..models import Usuario
from ..security import destino_seguro, ip_cliente
from ..services import auditoria

bp = Blueprint("auth", __name__)
log = logging.getLogger(__name__)

MENSAJE_LOGIN_FALLIDO = "Usuario o contraseña incorrectos."  # mismo mensaje en ambos casos


class LoginForm(FlaskForm):
    usuario = StringField("Usuario", validators=[DataRequired(), Length(max=50)])
    clave = PasswordField("Contraseña", validators=[DataRequired(), Length(max=200)])


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("vistas.dashboard"))

    form = LoginForm()
    error = None
    if request.args.get("error") == "sesion":
        error = "La sesión expiró. Vuelve a ingresar."

    if form.validate_on_submit():
        nombre = form.usuario.data.strip().lower()
        usuario = db.session.execute(
            db.select(Usuario).filter_by(usuario=nombre)
        ).scalar_one_or_none()

        if usuario and usuario.activo and usuario.check_password(form.clave.data):
            login_user(usuario)
            auditoria.registrar("LOGIN_OK", "usuarios", usuario.id, usuario_id=usuario.id)
            db.session.commit()
            destino = destino_seguro(request.args.get("next"), url_for("vistas.dashboard"))
            return redirect(destino)

        # No se revela si el usuario existe; se audita sin guardar la contraseña
        auditoria.registrar("LOGIN_FALLIDO", "usuarios", usuario.id if usuario else None,
                            detalle={"usuario_intentado": nombre[:50]},
                            usuario_id=usuario.id if usuario else None)
        db.session.commit()
        log.warning("Login fallido para '%s' desde %s", nombre[:50], ip_cliente())
        error = MENSAJE_LOGIN_FALLIDO

    status = 401 if error == MENSAJE_LOGIN_FALLIDO else 200
    return render_template("login.html", form=form, error=error), status


@bp.post("/logout")
def logout():
    # POST (con CSRF) para que un enlace externo no pueda cerrar la sesión
    if current_user.is_authenticated:
        auditoria.registrar("LOGOUT", "usuarios", current_user.id)
        db.session.commit()
        logout_user()
    return redirect(url_for("auth.login"))
