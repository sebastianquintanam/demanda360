"""API de catálogo e inventario (P0): productos, catálogos, conteos, ventas y movimientos.

Reglas comunes de los POST:
  · El rol se verifica aquí (ocultar un botón no es un control).
  · origen_ref hace la operación idempotente: si el formulario se reenvía, se
    responde 200 con lo que ya existe en vez de registrar dos veces.
  · El producto se bloquea (FOR UPDATE) antes de leer el saldo.
  · El registro y su fila de auditoría van en la misma transacción.
"""

import re

from flask import Blueprint, current_app, jsonify
from flask_login import current_user
from sqlalchemy import exc, text

from ..errors import ApiError
from ..extensions import db
from ..models import (Categoria, ConteoFisico, Movimiento, Producto, Proveedor,
                      SolicitudCliente, Usuario)
from ..security import ROL_PROPIETARIO, ROL_TRABAJADOR, es_propietario, requiere_rol
from ..services import alertas, auditoria
from ..services import inventario as inv
from ..services import validacion as v

bp = Blueprint("inventario", __name__, url_prefix="/api")

AMBOS = (ROL_PROPIETARIO, ROL_TRABAJADOR)
UNIDADES = ("unidad", "galon", "medio_galon", "cuarto_galon", "cunete", "litro", "kilogramo")


def _origen():
    return current_app.config["ORIGEN_DATOS"]


def _ref_en_uso(ref: str) -> ApiError:
    return ApiError(409, "ORIGEN_REF_EN_USO",
                    "Ese origen_ref ya se usó en otro tipo de registro. Recarga el formulario.",
                    {"origen_ref": "en_uso"})


# --- Catálogos -------------------------------------------------------------------

@bp.get("/catalogos")
@requiere_rol(*AMBOS)
def catalogos():
    """Listas para los formularios de Registro (categoría, proveedor, unidad)."""
    categorias = db.session.execute(db.select(Categoria).order_by(Categoria.nombre)).scalars()
    proveedores = db.session.execute(
        db.select(Proveedor).where(Proveedor.activo).order_by(Proveedor.nombre)).scalars()
    return jsonify(
        categorias=[{"id": c.id, "nombre": c.nombre} for c in categorias],
        proveedores=[{"id": p.id, "codigo": p.codigo, "nombre": p.nombre,
                      "plazo_entrega_dias": p.plazo_entrega_dias} for p in proveedores],
        unidades_medida=list(UNIDADES),
    )


# --- Productos ---------------------------------------------------------------------

@bp.get("/productos")
@requiere_rol(*AMBOS)
def listar_productos():
    campos = ("id", "sku", "nombre", "categoria", "proveedor", "plazo_entrega_dias", "presentacion",
              "unidad_medida", "umbral_reposicion", "saldo", "estado")
    return jsonify(origen_datos=_origen(),
                   productos=[{c: e[c] for c in campos} for e in inv.estados()])


def _producto_json(p: Producto) -> dict:
    return {
        "id": p.id, "sku": p.sku, "nombre": p.nombre, "categoria_id": p.categoria_id,
        "proveedor_id": p.proveedor_id, "marca": p.marca, "presentacion": p.presentacion,
        "unidad_medida": p.unidad_medida, "costo_compra": inv.numero(p.costo_compra),
        "precio_venta": inv.numero(p.precio_venta), "umbral_reposicion": p.umbral_reposicion,
        "activo": p.activo, "creado_en": p.creado_en.isoformat(timespec="seconds"),
    }


@bp.post("/productos")
@requiere_rol(ROL_PROPIETARIO, mensaje="Solo un propietario puede crear productos.")
def crear_producto():
    datos = v.cuerpo_json()
    sku = (v.texto(datos, "sku", maximo=30, minimo=3) or "").upper().replace(" ", "")
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9-]{2,29}", sku):
        raise ApiError(400, "VALIDACION", "El SKU solo admite letras, números y guiones (3 a 30).", {"sku": "formato"})
    nuevo = dict(
        sku=sku,
        nombre=v.texto(datos, "nombre", maximo=150, minimo=3),
        categoria_id=v.entero(datos, "categoria_id", minimo=1, maximo=None),
        proveedor_id=v.entero(datos, "proveedor_id", minimo=1, maximo=None),
        marca=v.texto(datos, "marca", maximo=80, requerido=False),
        presentacion=v.texto(datos, "presentacion", maximo=60),
        unidad_medida=v.opcion(datos, "unidad_medida", UNIDADES),
        costo_compra=v.dinero(datos, "costo_compra"),
        precio_venta=v.dinero(datos, "precio_venta"),
        umbral_reposicion=v.entero(datos, "umbral_reposicion", minimo=0, maximo=10_000),
    )
    if db.session.get(Categoria, nuevo["categoria_id"]) is None:
        raise ApiError(400, "VALIDACION", "La categoría no existe.", {"categoria_id": "no_existe"})
    proveedor = db.session.get(Proveedor, nuevo["proveedor_id"])
    if proveedor is None or not proveedor.activo:
        raise ApiError(400, "VALIDACION", "El proveedor no existe o está inactivo.", {"proveedor_id": "no_existe"})

    duplicado = ApiError(409, "SKU_DUPLICADO", f"Ya existe un producto con el SKU {sku}.", {"sku": "duplicado"})
    if db.session.execute(db.select(Producto.id).where(Producto.sku == sku)).first():
        raise duplicado
    producto = Producto(**nuevo)
    db.session.add(producto)
    try:
        db.session.flush()
    except exc.IntegrityError:  # otro propietario lo creó al mismo tiempo
        db.session.rollback()
        raise duplicado from None
    auditoria.registrar("PRODUCTO_CREADO", "productos", producto.id, {"sku": sku})
    db.session.commit()
    return jsonify({**_producto_json(producto), "saldo": None, "estado": "SIN_CONTEO"}), 201


@bp.get("/productos/<int:producto_id>")
@requiere_rol(*AMBOS)
def detalle_producto(producto_id: int):
    e = inv.estado_de(producto_id)
    producto = {c: e[c] for c in ("id", "sku", "nombre", "categoria", "proveedor", "plazo_entrega_dias",
                                  "presentacion", "unidad_medida", "umbral_reposicion", "saldo", "estado")}
    movimientos = db.session.execute(
        db.select(Movimiento, Usuario.usuario).join(Usuario, Usuario.id == Movimiento.usuario_id)
        .where(Movimiento.producto_id == producto_id)
        .order_by(Movimiento.fecha_hora.desc(), Movimiento.id.desc()).limit(10)
    ).all()
    conteo = db.session.execute(
        db.select(ConteoFisico, Usuario.usuario).join(Usuario, Usuario.id == ConteoFisico.usuario_id)
        .where(ConteoFisico.producto_id == producto_id)
        .order_by(ConteoFisico.fecha_hora.desc(), ConteoFisico.id.desc()).limit(1)
    ).first()
    # Atenciones con faltante a las que un cliente que regresa se puede enlazar
    faltantes = db.session.execute(text("""
        SELECT s.id AS solicitud_id, s.fecha_hora, s.cantidad_solicitada, s.cantidad_entregada,
               s.cantidad_solicitada - s.cantidad_entregada
                 - COALESCE((SELECT sum(r.cantidad_solicitada) FROM solicitudes_clientes r
                             WHERE r.solicitud_previa_id = s.id), 0) AS faltante_pendiente
        FROM solicitudes_clientes s
        WHERE s.producto_id = :id AND s.solicitud_previa_id IS NULL
          AND s.cantidad_entregada < s.cantidad_solicitada
          AND s.fecha_hora >= now() - interval '30 days'
        ORDER BY s.fecha_hora DESC
        LIMIT 10
    """), {"id": producto_id}).mappings().all()
    return jsonify(
        origen_datos=_origen(),
        producto=producto,
        ultimos_movimientos=[
            {"id": m.id, "tipo": m.tipo, "cantidad": m.cantidad,
             "fecha_hora": m.fecha_hora.isoformat(timespec="seconds"), "usuario": u,
             "justificacion": m.justificacion}
            for m, u in movimientos
        ],
        ultimo_conteo=None if conteo is None else {
            "cantidad_contada": conteo[0].cantidad_contada,
            "fecha_hora": conteo[0].fecha_hora.isoformat(timespec="seconds"),
            "usuario": conteo[1],
        },
        faltantes_pendientes=[
            {"solicitud_id": f["solicitud_id"], "fecha_hora": f["fecha_hora"].isoformat(timespec="seconds"),
             "cantidad_solicitada": f["cantidad_solicitada"], "cantidad_entregada": f["cantidad_entregada"],
             "faltante_pendiente": f["faltante_pendiente"]}
            for f in faltantes if f["faltante_pendiente"] > 0
        ],
    )


# --- Conteos -----------------------------------------------------------------------

def _conteo_json(c: ConteoFisico, saldo_anterior) -> tuple[dict, dict]:
    cuerpo = {"id": c.id, "producto_id": c.producto_id, "cantidad_contada": c.cantidad_contada,
              "fecha_hora": c.fecha_hora.isoformat(timespec="seconds"), "observaciones": c.observaciones}
    return cuerpo, inv.resumen_producto(c.producto_id, saldo_anterior)


@bp.post("/conteos")
@requiere_rol(*AMBOS)
def registrar_conteo():
    datos = v.cuerpo_json()
    producto_id = v.entero(datos, "producto_id", minimo=1, maximo=None)
    cantidad = v.entero(datos, "cantidad_contada", minimo=0,
                        mensaje="La cantidad contada debe ser un entero mayor o igual a 0.")
    observaciones = v.texto(datos, "observaciones", maximo=300, requerido=False)
    ref = v.origen_ref(datos)

    existente = db.session.execute(db.select(ConteoFisico).filter_by(origen_ref=ref)).scalar_one_or_none()
    if existente:
        cuerpo, producto = _conteo_json(existente, None)
        return jsonify({**cuerpo, "producto": producto, "duplicado": True}), 200

    inv.bloquear_producto(producto_id)
    saldo_antes = inv.saldo_actual(producto_id)
    conteo = ConteoFisico(producto_id=producto_id, cantidad_contada=cantidad, usuario_id=current_user.id,
                          observaciones=observaciones, origen_ref=ref)
    try:
        db.session.add(conteo)
        db.session.flush()
        auditoria.registrar("CONTEO_REGISTRADO", "conteos_fisicos", conteo.id, {
            "producto_id": producto_id, "contado": cantidad, "saldo_sistema": saldo_antes,
            "diferencia": None if saldo_antes is None else cantidad - saldo_antes})
        db.session.commit()
    except exc.IntegrityError:  # el mismo formulario llegó dos veces al mismo tiempo
        db.session.rollback()
        existente = db.session.execute(db.select(ConteoFisico).filter_by(origen_ref=ref)).scalar_one_or_none()
        if existente is None:
            raise
        cuerpo, producto = _conteo_json(existente, None)
        return jsonify({**cuerpo, "producto": producto, "duplicado": True}), 200
    cuerpo, producto = _conteo_json(conteo, saldo_antes)
    return jsonify({**cuerpo, "producto": producto}), 201


# --- Ventas (atención al cliente) ----------------------------------------------------

def _venta_json(s: SolicitudCliente, saldo_anterior, alerta) -> dict:
    return {
        "solicitud_id": s.id,
        "movimiento_id": s.movimiento_id,
        "solicitud_previa_id": s.solicitud_previa_id,
        "no_atendida": s.cantidad_solicitada - s.cantidad_entregada,
        "producto": inv.resumen_producto(s.producto_id, saldo_anterior),
        "alerta": None if alerta is None else {"evento_id": str(alerta.evento_id), "estado": alerta.estado},
    }


def _validar_regreso(previa_id: int, producto_id: int, solicitada: int) -> None:
    """Cliente que regresa: se enlaza a la atención ORIGINAL con faltante, del mismo producto."""
    previa = db.session.get(SolicitudCliente, previa_id)
    if previa is None or previa.producto_id != producto_id:
        raise ApiError(400, "VALIDACION", "La atención original no existe o es de otro producto.",
                       {"solicitud_previa_id": "no_existe"})
    if previa.solicitud_previa_id is not None:
        raise ApiError(400, "VALIDACION", "Enlaza el regreso a la atención original, no a otro regreso.",
                       {"solicitud_previa_id": "no_es_original"})
    ya_regreso = db.session.execute(
        db.select(db.func.coalesce(db.func.sum(SolicitudCliente.cantidad_solicitada), 0))
        .where(SolicitudCliente.solicitud_previa_id == previa_id)).scalar()
    pendiente = previa.cantidad_solicitada - previa.cantidad_entregada - ya_regreso
    if solicitada > pendiente:
        raise ApiError(400, "VALIDACION",
                       f"A esa atención le quedan {max(pendiente, 0)} unidades pendientes; no se pueden pedir {solicitada}.",
                       {"cantidad_solicitada": "supera_faltante"})


@bp.post("/ventas")
@requiere_rol(*AMBOS)
def registrar_venta():
    datos = v.cuerpo_json()
    producto_id = v.entero(datos, "producto_id", minimo=1, maximo=None)
    solicitada = v.entero(datos, "cantidad_solicitada", minimo=1,
                          mensaje="La cantidad solicitada debe ser un entero mayor que 0.")
    entregada = v.entero(datos, "cantidad_entregada", minimo=0, maximo=solicitada,
                         mensaje="La cantidad entregada debe ser un entero entre 0 y la cantidad solicitada.")
    previa_id = v.entero(datos, "solicitud_previa_id", minimo=1, maximo=None, requerido=False)
    ref = v.origen_ref(datos)

    existente = db.session.execute(db.select(SolicitudCliente).filter_by(origen_ref=ref)).scalar_one_or_none()
    if existente:
        alerta = db.session.execute(db.select(alertas.AlertaEnviada).filter_by(
            movimiento_id=existente.movimiento_id)).scalar_one_or_none() if existente.movimiento_id else None
        return jsonify({**_venta_json(existente, None, alerta), "duplicado": True}), 200

    producto = inv.bloquear_producto(producto_id)
    saldo_antes = inv.saldo_actual(producto_id)
    if entregada > 0:
        inv.exigir_conteo(saldo_antes, producto["sku"])
        if entregada > saldo_antes:
            raise ApiError(409, "STOCK_INSUFICIENTE",
                           f"Saldo disponible: {saldo_antes}. No se puede entregar {entregada}.",
                           {"cantidad_entregada": "supera_saldo"})
    if previa_id is not None:
        _validar_regreso(previa_id, producto_id, solicitada)

    movimiento = alerta = None
    try:
        if entregada > 0:
            movimiento = Movimiento(producto_id=producto_id, tipo="VENTA", cantidad=entregada,
                                    usuario_id=current_user.id, origen_ref=ref)
            db.session.add(movimiento)
            db.session.flush()
        solicitud = SolicitudCliente(producto_id=producto_id, cantidad_solicitada=solicitada,
                                     cantidad_entregada=entregada, usuario_id=current_user.id,
                                     movimiento_id=movimiento.id if movimiento else None,
                                     solicitud_previa_id=previa_id, origen_ref=ref)
        db.session.add(solicitud)
        db.session.flush()

        detalle = {"producto_id": producto_id, "solicitada": solicitada, "entregada": entregada}
        if previa_id:
            detalle["solicitud_previa_id"] = previa_id
        if movimiento:
            auditoria.registrar("VENTA_REGISTRADA", "movimientos", movimiento.id, detalle)
        else:
            auditoria.registrar("ATENCION_SIN_ENTREGA", "solicitudes_clientes", solicitud.id, detalle)

        if movimiento and alertas.cruza_umbral(saldo_antes, saldo_antes - entregada, producto["umbral_reposicion"]):
            alerta = alertas.crear(producto_id, movimiento.id, saldo_antes - entregada, producto["umbral_reposicion"])
            db.session.flush()
            auditoria.registrar("ALERTA_CREADA", "alertas_enviadas", alerta.id,
                                {"producto_id": producto_id, "saldo": alerta.saldo, "umbral": alerta.umbral})
        db.session.commit()
    except exc.IntegrityError:  # el mismo formulario llegó dos veces al mismo tiempo
        db.session.rollback()
        existente = db.session.execute(db.select(SolicitudCliente).filter_by(origen_ref=ref)).scalar_one_or_none()
        if existente is None:
            raise _ref_en_uso(ref) from None
        return jsonify({**_venta_json(existente, None, None), "duplicado": True}), 200

    # La venta ya quedó guardada: el correo se intenta después y nunca la deshace
    if alerta is not None:
        alerta = alertas.enviar(alerta.id)
    return jsonify(_venta_json(solicitud, saldo_antes, alerta)), 201


# --- Entradas y ajustes ----------------------------------------------------------------

def _movimiento_json(m: Movimiento, saldo_anterior) -> dict:
    return {"id": m.id, "producto_id": m.producto_id, "tipo": m.tipo, "cantidad": m.cantidad,
            "fecha_hora": m.fecha_hora.isoformat(timespec="seconds"), "justificacion": m.justificacion,
            "producto": inv.resumen_producto(m.producto_id, saldo_anterior)}


@bp.post("/movimientos")
@requiere_rol(*AMBOS)
def registrar_movimiento():
    datos = v.cuerpo_json()
    tipo = v.opcion(datos, "tipo", ("ENTRADA", "AJUSTE"))
    if tipo == "AJUSTE" and not es_propietario():
        raise ApiError(403, "SIN_PERMISO", "Solo un propietario puede registrar ajustes.")
    producto_id = v.entero(datos, "producto_id", minimo=1, maximo=None)
    if tipo == "ENTRADA":
        cantidad = v.entero(datos, "cantidad", minimo=1,
                            mensaje="La cantidad de una entrada debe ser un entero mayor que 0.")
        justificacion = v.texto(datos, "justificacion", maximo=500, requerido=False)
    else:
        cantidad = v.entero(datos, "cantidad", minimo=-v.MAXIMO_CANTIDAD,
                            mensaje="El ajuste debe ser un entero distinto de 0 (+ suma, − resta).")
        if cantidad == 0:
            raise ApiError(400, "VALIDACION", "El ajuste debe ser un entero distinto de 0 (+ suma, − resta).",
                           {"cantidad": "rango"})
        justificacion = v.texto(datos, "justificacion", maximo=500, minimo=10)
    ref = v.origen_ref(datos)

    existente = db.session.execute(db.select(Movimiento).filter_by(origen_ref=ref)).scalar_one_or_none()
    if existente:
        if existente.tipo != tipo:
            raise _ref_en_uso(ref)
        return jsonify({**_movimiento_json(existente, None), "duplicado": True}), 200

    producto = inv.bloquear_producto(producto_id)
    saldo_antes = inv.exigir_conteo(inv.saldo_actual(producto_id), producto["sku"])
    if saldo_antes + cantidad < 0:
        raise ApiError(409, "STOCK_INSUFICIENTE",
                       f"Saldo disponible: {saldo_antes}. Un ajuste de {cantidad} lo dejaría negativo.",
                       {"cantidad": "supera_saldo"})
    movimiento = Movimiento(producto_id=producto_id, tipo=tipo, cantidad=cantidad, usuario_id=current_user.id,
                            origen_ref=ref, justificacion=justificacion)
    try:
        db.session.add(movimiento)
        db.session.flush()
        auditoria.registrar("ENTRADA_REGISTRADA" if tipo == "ENTRADA" else "AJUSTE_REGISTRADO", "movimientos",
                            movimiento.id, {"producto_id": producto_id, "cantidad": cantidad,
                                            "saldo_anterior": saldo_antes})
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        existente = db.session.execute(db.select(Movimiento).filter_by(origen_ref=ref)).scalar_one_or_none()
        if existente is None:
            raise
        return jsonify({**_movimiento_json(existente, None), "duplicado": True}), 200
    return jsonify(_movimiento_json(movimiento, saldo_antes)), 201
