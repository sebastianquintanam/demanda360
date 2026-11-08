"""Dashboard y análisis de rotación. Solo leen: los cálculos viven en 02_vistas.sql.

KPI: periodo de 30 días que termina en el corte (?corte=AAAA-MM-DD; por defecto
fn_corte() = 2026-09-30). Saldo y estado: los de hoy. Así una venta en vivo
cambia la tabla de inventario y los críticos, pero no los KPI de septiembre.
"""

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import text

from ..extensions import db
from ..security import ROL_PROPIETARIO, ROL_TRABAJADOR, requiere_rol
from ..services import inventario as inv
from ..services import validacion as v

bp = Blueprint("analitica", __name__, url_prefix="/api")

# Metas preliminares del plan (sección 6). Ninguna se presenta como logro.
METAS = {"KPI1": "−20 % vs. línea base", "KPI2": "−20 % vs. línea base", "KPI3": "−10 % vs. línea base",
         "KPI4": "Sin meta hasta tener línea base", "KPI5": "Sin meta hasta tener línea base"}


def _kpis(corte) -> list[dict]:
    return [dict(f) for f in db.session.execute(
        text("SELECT * FROM fn_kpi_resumen(COALESCE(CAST(:corte AS date), fn_corte()))"), {"corte": corte}
    ).mappings()]


@bp.get("/dashboard")
@requiere_rol(ROL_PROPIETARIO, ROL_TRABAJADOR)
def dashboard():
    corte = v.fecha_corte(request.args.get("corte"))
    kpis = _kpis(corte)
    productos = inv.estados(corte)
    orden = {"AGOTADO": 0, "CRITICO": 1}
    criticos = sorted((p for p in productos if p["estado"] in orden), key=lambda p: (orden[p["estado"]], p["id"]))
    return jsonify(
        corte=kpis[0]["corte"].isoformat(),
        periodo={"desde": kpis[0]["periodo_desde"].isoformat(), "hasta": kpis[0]["periodo_hasta"].isoformat()},
        origen_datos=current_app.config["ORIGEN_DATOS"],
        kpis=[
            {"codigo": k["codigo"], "nombre": k["nombre"], "valor": inv.numero(k["valor"]), "unidad": k["unidad"],
             "numerador": inv.numero(k["numerador"]), "denominador": k["denominador"], "detalle": k["detalle"],
             "meta": METAS[k["codigo"]], "variacion": None}
            for k in kpis if k["codigo"] in ("KPI1", "KPI2", "KPI3")
        ],
        criticos=[{c: p[c] for c in ("id", "sku", "nombre", "saldo", "umbral_reposicion", "estado",
                                     "plazo_entrega_dias")} for p in criticos],
        inventario=[{c: p[c] for c in ("id", "sku", "nombre", "saldo", "vendidas_30d", "no_atendidas_30d",
                                       "plazo_entrega_dias", "estado")} for p in productos],
    )


@bp.get("/analisis/rotacion")
@requiere_rol(ROL_PROPIETARIO, ROL_TRABAJADOR)
def rotacion():
    corte = v.fecha_corte(request.args.get("corte"))
    corte_efectivo = db.session.execute(
        text("SELECT COALESCE(CAST(:corte AS date), fn_corte())"), {"corte": corte}).scalar()
    campos = ("id", "sku", "nombre", "saldo", "vendidas_30d", "no_atendidas_30d", "dias_con_registro",
              "demanda_diaria", "cobertura_dias", "plazo_entrega_dias", "estado")
    return jsonify(corte=corte_efectivo.isoformat(), origen_datos=current_app.config["ORIGEN_DATOS"],
                   productos=[{c: p[c] for c in campos} for p in inv.estados(corte)])
