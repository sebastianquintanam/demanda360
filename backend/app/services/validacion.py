"""Validación de entradas de la API. Cada error dice qué campo falló y por qué,
con el formato del contrato: 400 VALIDACION y campos {"campo": "motivo"}.

Motivos usados: requerido, entero, numero, rango, texto, longitud, formato, lista.
"""

import re
from datetime import date
from decimal import Decimal, InvalidOperation

from flask import request

from ..errors import ApiError

MAXIMO_CANTIDAD = 100_000
_ORIGEN_REF = re.compile(r"^[A-Za-z0-9_.:-]{1,64}$")


def _falla(campo: str, motivo: str, mensaje: str):
    raise ApiError(400, "VALIDACION", mensaje, {campo: motivo})


def cuerpo_json() -> dict:
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        raise ApiError(400, "VALIDACION", "El cuerpo debe ser un objeto JSON.", {"cuerpo": "formato"})
    return datos


def entero(datos: dict, campo: str, minimo: int | None = None, maximo: int | None = MAXIMO_CANTIDAD,
           requerido: bool = True, mensaje: str | None = None) -> int | None:
    valor = datos.get(campo)
    if valor is None or valor == "":
        if requerido:
            _falla(campo, "requerido", f"El campo {campo} es obligatorio.")
        return None
    # bool es subclase de int en Python: true/false no son cantidades
    if isinstance(valor, bool) or not isinstance(valor, int):
        if isinstance(valor, str) and re.fullmatch(r"-?\d+", valor.strip()):
            valor = int(valor.strip())
        else:
            _falla(campo, "entero", mensaje or f"{campo} debe ser un número entero.")
    if (minimo is not None and valor < minimo) or (maximo is not None and valor > maximo):
        _falla(campo, "rango", mensaje or f"{campo} está fuera del rango permitido.")
    return valor


def dinero(datos: dict, campo: str) -> Decimal:
    valor = datos.get(campo)
    if valor is None or valor == "" or isinstance(valor, bool):
        _falla(campo, "requerido", f"El campo {campo} es obligatorio.")
    try:
        numero = Decimal(str(valor))
    except InvalidOperation:
        _falla(campo, "numero", f"{campo} debe ser un número.")
    if not numero.is_finite() or numero < 0 or numero > Decimal("9999999999.99"):
        _falla(campo, "rango", f"{campo} debe ser mayor o igual a 0.")
    if numero.as_tuple().exponent < -2:
        _falla(campo, "formato", f"{campo} admite máximo 2 decimales.")
    return numero


def texto(datos: dict, campo: str, maximo: int, minimo: int = 1, requerido: bool = True) -> str | None:
    valor = datos.get(campo)
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        if requerido:
            _falla(campo, "requerido", f"El campo {campo} es obligatorio.")
        return None
    if not isinstance(valor, str):
        _falla(campo, "texto", f"{campo} debe ser texto.")
    valor = " ".join(valor.split())  # sin espacios repetidos ni saltos de línea
    if not minimo <= len(valor) <= maximo:
        _falla(campo, "longitud", f"{campo} debe tener entre {minimo} y {maximo} caracteres.")
    return valor


def opcion(datos: dict, campo: str, opciones: tuple) -> str:
    valor = datos.get(campo)
    if valor is None or valor == "":
        _falla(campo, "requerido", f"El campo {campo} es obligatorio.")
    if valor not in opciones:
        _falla(campo, "lista", f"{campo} debe ser uno de: {', '.join(opciones)}.")
    return valor


def origen_ref(datos: dict, requerido: bool = True) -> str | None:
    """Identificador del formulario (UUID o folio manual). Evita registrar dos veces lo mismo."""
    valor = datos.get("origen_ref")
    if valor is None or valor == "":
        if requerido:
            _falla("origen_ref", "requerido", "Falta origen_ref: el formulario debe generarlo al abrirse.")
        return None
    if not isinstance(valor, str) or not _ORIGEN_REF.match(valor):
        _falla("origen_ref", "formato", "origen_ref solo admite letras, números y - _ . : (máximo 64).")
    return valor


def fecha_corte(argumento: str | None) -> date | None:
    """?corte=AAAA-MM-DD. None = corte por defecto de la base (fn_corte())."""
    if not argumento:
        return None
    try:
        corte = date.fromisoformat(argumento)
    except ValueError:
        _falla("corte", "formato", "corte debe tener el formato AAAA-MM-DD.")
    if corte > date.today():
        _falla("corte", "rango", "corte no puede ser una fecha futura.")
    return corte
