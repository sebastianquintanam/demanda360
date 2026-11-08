"""Reglas de inventario del lado de Flask.

El saldo y el estado NO se calculan aquí: se leen de las funciones de
database/sql/02_vistas.sql (una sola definición para Flask, Power BI y Excel).
Aquí vive lo que necesita una transacción: bloquear el producto, validar contra
el saldo, registrar y auditar en la misma transacción.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import text

from ..errors import ApiError
from ..extensions import db


def numero(valor):
    """Decimal de la base → número JSON (46000.00 → 46000; 0.87 → 0.87)."""
    if valor is None:
        return None
    if isinstance(valor, Decimal):
        return int(valor) if valor == valor.to_integral_value() else float(valor)
    return valor


def bloquear_producto(producto_id: int) -> dict:
    """SELECT … FOR UPDATE: dos operaciones sobre el mismo producto se atienden una
    detrás de otra, así dos ventas simultáneas no pueden dejar el saldo negativo."""
    fila = db.session.execute(
        text("SELECT id, sku, umbral_reposicion, activo FROM productos WHERE id = :id FOR UPDATE"),
        {"id": producto_id},
    ).mappings().first()
    if fila is None or not fila["activo"]:
        raise ApiError(404, "NO_ENCONTRADO", f"El producto {producto_id} no existe o está inactivo.",
                       {"producto_id": "no_existe"})
    return dict(fila)


def saldo_actual(producto_id: int) -> int | None:
    """Saldo con todo lo registrado (también lo de la transacción en curso). None = sin conteo."""
    return db.session.execute(
        text("SELECT saldo FROM fn_saldos('infinity') WHERE producto_id = :id"), {"id": producto_id}
    ).scalar()


def estados(corte: date | None = None, producto_id: int | None = None) -> list[dict]:
    """Saldo de hoy + estado, con la rotación del periodo de corte (por defecto fn_corte())."""
    sql = """
        SELECT p.id, p.sku, p.nombre, c.nombre AS categoria, pr.nombre AS proveedor,
               pr.plazo_entrega_dias, p.presentacion, p.unidad_medida, p.umbral_reposicion,
               e.saldo, e.estado, e.dias_con_registro, e.vendidas_30d, e.no_atendidas_30d,
               e.demanda_diaria, e.cobertura_dias
        FROM productos p
        JOIN categorias c ON c.id = p.categoria_id
        JOIN proveedores pr ON pr.id = p.proveedor_id
        JOIN fn_estado_productos(COALESCE(CAST(:corte AS date), fn_corte()), 'infinity') e ON e.producto_id = p.id
        WHERE p.activo AND (CAST(:id AS bigint) IS NULL OR p.id = CAST(:id AS bigint))
        ORDER BY p.id
    """
    filas = db.session.execute(text(sql), {"corte": corte, "id": producto_id}).mappings().all()
    return [{k: numero(v) for k, v in f.items()} for f in filas]


def estado_de(producto_id: int) -> dict:
    filas = estados(producto_id=producto_id)
    if not filas:
        raise ApiError(404, "NO_ENCONTRADO", f"El producto {producto_id} no existe.", {"producto_id": "no_existe"})
    return filas[0]


def resumen_producto(producto_id: int, saldo_anterior: int | None) -> dict:
    """Bloque "producto" de las respuestas de conteo, venta y movimiento."""
    e = estado_de(producto_id)
    return {
        "id": e["id"],
        "sku": e["sku"],
        "saldo_anterior": saldo_anterior,
        "saldo_actual": e["saldo"],
        "umbral_reposicion": e["umbral_reposicion"],
        "estado": e["estado"],
    }


def exigir_conteo(saldo: int | None, sku: str) -> int:
    if saldo is None:
        raise ApiError(409, "SIN_CONTEO",
                       f"{sku} no tiene conteo físico. Registra un conteo antes de mover inventario.",
                       {"producto_id": "sin_conteo"})
    return saldo
