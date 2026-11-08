"""API de planificación (P1): cantidades sugeridas y pedidos con aprobación del propietario.

Ciclo de un pedido (plan, sección 4):
    BORRADOR ──aprobar──▶ APROBADO ──▶ ENVIADO ──▶ CONFIRMADO
        └──────────────┴──────────────┴──▶ CANCELADO ──(reintento)──▶ pedido nuevo, intento + 1
  · Crear un borrador: ambos roles. Aprobar, enviar, confirmar y cancelar: solo el propietario.
  · Solo se envía lo aprobado. Cualquier otro salto responde 409 TRANSICION_INVALIDA.
  · El reintento con otro proveedor nace APROBADO por el propietario que lo pidió,
    enlazado con pedido_anterior_id: así el KPI 5 cuenta la cadena una sola vez.
  · La cantidad sugerida la calcula el servidor (fn_sugeridos), nunca se toma del cliente.
  · Confirmar un pedido NO suma inventario: la mercancía entra cuando llega (Registro → Entrada).
"""

from datetime import date

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user
from sqlalchemy import text

from ..errors import ApiError
from ..extensions import db
from ..models import Pedido, PedidoDetalle, Producto, Proveedor
from ..security import ROL_PROPIETARIO, ROL_TRABAJADOR, requiere_rol
from ..services import auditoria
from ..services import inventario as inv
from ..services import validacion as v

bp = Blueprint("pedidos", __name__, url_prefix="/api")

SOLO_PROPIETARIO = "Solo un propietario puede {}."
REGLA = ("Sugerido = máx(0, techo(demanda diaria × cobertura − saldo)); demanda diaria = "
         "(vendidas + no atendidas en 30 días) / 30. Con datos insuficientes la cantidad es manual. "
         "El propietario aprueba.")
MAX_LINEAS = 50


def _cobertura(valor) -> int:
    return v.entero({"cobertura": valor if valor not in (None, "") else 14}, "cobertura", minimo=1, maximo=90,
                    mensaje="La cobertura debe ser un entero entre 1 y 90 días.")


def _sugeridos(cobertura: int) -> list[dict]:
    filas = db.session.execute(text("""
        SELECT p.id, p.sku, p.nombre, pr.id AS proveedor_id, pr.nombre AS proveedor, pr.plazo_entrega_dias,
               s.saldo, s.demanda_diaria, s.cobertura_dias, s.sugerido, s.formula, s.regla_version
        FROM productos p
        JOIN proveedores pr ON pr.id = p.proveedor_id
        JOIN fn_sugeridos(fn_corte(), 'infinity', :cobertura) s ON s.producto_id = p.id
        WHERE p.activo
        ORDER BY p.id
    """), {"cobertura": cobertura}).mappings().all()
    return [{k: inv.numero(val) for k, val in f.items()} for f in filas]


@bp.get("/sugeridos")
@requiere_rol(ROL_PROPIETARIO, mensaje=SOLO_PROPIETARIO.format("ver las cantidades sugeridas"))
def sugeridos():
    cobertura = _cobertura(request.args.get("cobertura"))
    productos = _sugeridos(cobertura)
    corte = db.session.execute(text("SELECT fn_corte()")).scalar()
    return jsonify(
        corte=corte.isoformat(),
        origen_datos=current_app.config["ORIGEN_DATOS"],
        cobertura_dias=cobertura,
        regla=REGLA,
        referencias_prioritarias=sum(1 for p in productos if (p["sugerido"] or 0) > 0),
        total_sugerido=sum(p["sugerido"] or 0 for p in productos),
        productos=productos,
    )


# --- Pedidos -----------------------------------------------------------------------------

def _iso(valor):
    return None if valor is None else valor.isoformat(timespec="seconds") if hasattr(valor, "hour") else valor.isoformat()


def _pedido_json(p: Pedido) -> dict:
    proveedor = db.session.get(Proveedor, p.proveedor_id)
    productos = {pr.id: pr for pr in db.session.execute(
        db.select(Producto).where(Producto.id.in_([d.producto_id for d in p.detalles]))).scalars()}
    horas = None
    if p.estado == "ENVIADO" and p.fecha_respuesta is None:
        horas = db.session.execute(text("SELECT round(extract(epoch FROM now() - :envio) / 3600.0, 1)"),
                                   {"envio": p.fecha_envio}).scalar()
    return {
        "id": p.id,
        "proveedor_id": p.proveedor_id,
        "proveedor": proveedor.nombre,
        "plazo_entrega_dias": proveedor.plazo_entrega_dias,
        "estado": p.estado,
        "numero_intento": p.numero_intento,
        "pedido_anterior_id": p.pedido_anterior_id,
        "reintento_id": db.session.execute(
            db.select(Pedido.id).where(Pedido.pedido_anterior_id == p.id)).scalar(),
        "fecha_creacion": _iso(p.fecha_creacion),
        "fecha_aprobacion": _iso(p.fecha_aprobacion),
        "fecha_envio": _iso(p.fecha_envio),
        "fecha_respuesta": _iso(p.fecha_respuesta),
        "fecha_entrega_estimada": _iso(p.fecha_entrega_estimada),
        "horas_esperando": inv.numero(horas),
        "motivo_cancelacion": p.motivo_cancelacion,
        "detalles": [
            {"producto_id": d.producto_id, "sku": productos[d.producto_id].sku,
             "nombre": productos[d.producto_id].nombre,
             "cantidad_sugerida": d.cantidad_sugerida, "cantidad_solicitada": d.cantidad_solicitada}
            for d in sorted(p.detalles, key=lambda d: d.producto_id)
        ],
    }


@bp.get("/pedidos")
@requiere_rol(ROL_PROPIETARIO, ROL_TRABAJADOR)
def listar_pedidos():
    pedidos = db.session.execute(db.select(Pedido).order_by(Pedido.id.desc()).limit(100)).scalars().all()
    return jsonify(origen_datos=current_app.config["ORIGEN_DATOS"], pedidos=[_pedido_json(p) for p in pedidos])


def _proveedor_activo(proveedor_id: int, campo: str) -> Proveedor:
    proveedor = db.session.get(Proveedor, proveedor_id)
    if proveedor is None or not proveedor.activo:
        raise ApiError(400, "VALIDACION", "El proveedor no existe o está inactivo.", {campo: "no_existe"})
    return proveedor


@bp.post("/pedidos")
@requiere_rol(ROL_PROPIETARIO, ROL_TRABAJADOR)
def crear_pedido():
    datos = v.cuerpo_json()
    proveedor_id = v.entero(datos, "proveedor_id", minimo=1, maximo=None)
    _proveedor_activo(proveedor_id, "proveedor_id")
    cobertura = _cobertura(datos.get("cobertura_dias"))
    lineas = datos.get("detalles")
    if not isinstance(lineas, list) or not 1 <= len(lineas) <= MAX_LINEAS:
        raise ApiError(400, "VALIDACION", f"El pedido necesita entre 1 y {MAX_LINEAS} productos.", {"detalles": "rango"})

    sugeridos = {s["id"]: s for s in _sugeridos(cobertura)}
    vistos, detalles = set(), []
    for i, linea in enumerate(lineas):
        if not isinstance(linea, dict):
            raise ApiError(400, "VALIDACION", "Cada línea debe tener producto_id y cantidad_solicitada.",
                           {f"detalles[{i}]": "formato"})
        producto_id = v.entero(linea, "producto_id", minimo=1, maximo=None)
        cantidad = v.entero(linea, "cantidad_solicitada", minimo=1,
                            mensaje="La cantidad a pedir debe ser un entero mayor que 0.")
        if producto_id not in sugeridos:
            raise ApiError(400, "VALIDACION", f"El producto {producto_id} no existe o está inactivo.",
                           {f"detalles[{i}].producto_id": "no_existe"})
        if producto_id in vistos:
            raise ApiError(400, "VALIDACION", f"{sugeridos[producto_id]['sku']} está repetido en el pedido.",
                           {f"detalles[{i}].producto_id": "duplicado"})
        vistos.add(producto_id)
        detalles.append(PedidoDetalle(producto_id=producto_id, cantidad_solicitada=cantidad,
                                      cantidad_sugerida=sugeridos[producto_id]["sugerido"]))

    pedido = Pedido(proveedor_id=proveedor_id, creado_por=current_user.id, detalles=detalles)
    db.session.add(pedido)
    db.session.flush()
    auditoria.registrar("PEDIDO_CREADO", "pedidos", pedido.id, {
        "proveedor_id": proveedor_id, "cobertura_dias": cobertura,
        "lineas": [{"producto_id": d.producto_id, "sugerida": d.cantidad_sugerida,
                    "solicitada": d.cantidad_solicitada} for d in detalles]})
    db.session.commit()
    return jsonify(_pedido_json(pedido)), 201


def _bloquear_pedido(pedido_id: int) -> Pedido:
    pedido = db.session.get(Pedido, pedido_id, with_for_update=True)
    if pedido is None:
        raise ApiError(404, "NO_ENCONTRADO", f"El pedido {pedido_id} no existe.")
    return pedido


def _transicion_invalida(pedido: Pedido, destino: str) -> ApiError:
    return ApiError(409, "TRANSICION_INVALIDA",
                    f"El pedido {pedido.id} está {pedido.estado}; no puede pasar a {destino}.",
                    {"estado": "transicion_invalida"})


@bp.post("/pedidos/<int:pedido_id>/aprobar")
@requiere_rol(ROL_PROPIETARIO, mensaje=SOLO_PROPIETARIO.format("aprobar pedidos"))
def aprobar_pedido(pedido_id: int):
    pedido = _bloquear_pedido(pedido_id)
    if pedido.estado != "BORRADOR":
        raise _transicion_invalida(pedido, "APROBADO")
    pedido.estado = "APROBADO"
    pedido.aprobado_por = current_user.id
    pedido.fecha_aprobacion = db.func.now()
    auditoria.registrar("PEDIDO_APROBADO", "pedidos", pedido.id, {"proveedor_id": pedido.proveedor_id})
    db.session.commit()
    return jsonify(_pedido_json(pedido)), 200


# Desde qué estados se puede llegar a cada destino
TRANSICIONES = {"ENVIADO": ("APROBADO",), "CONFIRMADO": ("ENVIADO",),
                "CANCELADO": ("BORRADOR", "APROBADO", "ENVIADO")}


@bp.post("/pedidos/<int:pedido_id>/estado")
@requiere_rol(ROL_PROPIETARIO, mensaje=SOLO_PROPIETARIO.format("cambiar el estado de un pedido"))
def cambiar_estado(pedido_id: int):
    datos = v.cuerpo_json()
    destino = v.opcion(datos, "estado", tuple(TRANSICIONES))
    pedido = _bloquear_pedido(pedido_id)
    if pedido.estado not in TRANSICIONES[destino]:
        raise _transicion_invalida(pedido, destino)

    detalle_auditoria = {"desde": pedido.estado, "hasta": destino}
    reintento = None
    if destino == "ENVIADO":
        pedido.fecha_envio = db.func.now()
    elif destino == "CONFIRMADO":
        pedido.fecha_respuesta = db.func.now()
        entrega = datos.get("fecha_entrega_estimada")
        if entrega:
            try:
                entrega = date.fromisoformat(entrega)
            except (TypeError, ValueError):
                raise ApiError(400, "VALIDACION", "fecha_entrega_estimada debe tener el formato AAAA-MM-DD.",
                               {"fecha_entrega_estimada": "formato"}) from None
        else:  # hoy en Bogotá + plazo del proveedor
            entrega = db.session.execute(text(
                "SELECT (now() AT TIME ZONE 'America/Bogota')::date + plazo_entrega_dias FROM proveedores WHERE id = :id"
            ), {"id": pedido.proveedor_id}).scalar()
        pedido.fecha_entrega_estimada = entrega
        detalle_auditoria["fecha_entrega_estimada"] = entrega.isoformat()
    else:  # CANCELADO
        pedido.motivo_cancelacion = v.texto(datos, "motivo_cancelacion", maximo=300, minimo=5)
        detalle_auditoria["motivo"] = pedido.motivo_cancelacion
        otro = v.entero(datos, "reintentar_con_proveedor_id", minimo=1, maximo=None, requerido=False)
        if otro is not None:
            if otro == pedido.proveedor_id:
                raise ApiError(400, "VALIDACION", "El reintento debe ser con otro proveedor.",
                               {"reintentar_con_proveedor_id": "mismo_proveedor"})
            _proveedor_activo(otro, "reintentar_con_proveedor_id")
            reintento = Pedido(
                proveedor_id=otro, estado="APROBADO", numero_intento=pedido.numero_intento + 1,
                pedido_anterior_id=pedido.id, creado_por=current_user.id, aprobado_por=current_user.id,
                fecha_aprobacion=db.func.now(),
                detalles=[PedidoDetalle(producto_id=d.producto_id, cantidad_sugerida=d.cantidad_sugerida,
                                        cantidad_solicitada=d.cantidad_solicitada) for d in pedido.detalles])
    pedido.estado = destino
    auditoria.registrar(f"PEDIDO_{destino}", "pedidos", pedido.id, detalle_auditoria)
    if reintento is not None:
        db.session.add(reintento)
        db.session.flush()
        auditoria.registrar("PEDIDO_REINTENTO", "pedidos", reintento.id, {
            "pedido_anterior_id": pedido.id, "proveedor_id": reintento.proveedor_id,
            "numero_intento": reintento.numero_intento})
    db.session.commit()
    cuerpo = _pedido_json(pedido)
    if reintento is not None:
        cuerpo["reintento"] = _pedido_json(reintento)
    return jsonify(cuerpo), 200
