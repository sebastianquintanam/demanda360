"""Rutas que muestran las plantillas Jinja. Las pantallas leen sus datos de /api
desde JavaScript (static/js/api.js); aquí no se calcula ninguna regla de negocio."""

from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_required

bp = Blueprint("vistas", __name__)


@bp.get("/")
def inicio():
    return redirect(url_for("vistas.dashboard"))


@bp.get("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", activo="dashboard")


@bp.get("/registro")
@login_required
def registro():
    return render_template("registro.html", activo="registro")


@bp.get("/planificacion")
@login_required
def planificacion():
    return render_template("planificacion.html", activo="planificacion")
