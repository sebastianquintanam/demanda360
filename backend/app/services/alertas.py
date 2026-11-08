"""Alerta de stock crítico: Flask registra, n8n solo envía el correo.

Contrato con n8n (cerrado el 8 nov 2026 con el Rol 2):
  · POST a N8N_WEBHOOK_URL con la cabecera X-Demanda360-Token = N8N_WEBHOOK_TOKEN.
  · n8n responde 200 con {"ok": true, ...} SOLO después de enviar el correo;
    502 con {"ok": false, "error": "..."} si falla el envío; 403 si el token no sirve.
  · El estado vive en PostgreSQL (alertas_enviadas). n8n no guarda nada ni descarta
    duplicados: preferimos un correo repetido a una alerta perdida.
  · ENVIADA solo con 200 + ok = true. Cualquier otra cosa (502, 403, tiempo agotado,
    n8n apagado) → FALLIDA, intentos + 1 y el error en ultimo_error.
  · `flask reintentar-alertas` reenvía con el MISMO evento_id, máximo 3 intentos.
  · Una alerta ENVIADA nunca se reenvía.

La alerta nace dentro de la transacción de la venta (fila PENDIENTE) y se envía
DESPUÉS del commit: si el correo falla, la venta ya quedó guardada.
"""

import logging
import uuid
from datetime import datetime, timezone

import requests
from flask import current_app
from sqlalchemy import text

from ..extensions import db
from ..models import AlertaEnviada, Producto, Proveedor

log = logging.getLogger(__name__)

MAX_INTENTOS = 3


def cruza_umbral(saldo_antes: int, saldo_despues: int, umbral: int) -> bool:
    """Solo la venta que cruza el umbral genera alerta; las siguientes bajo el umbral no."""
    return saldo_antes > umbral >= saldo_despues


def crear(producto_id: int, movimiento_id: int, saldo: int, umbral: int) -> AlertaEnviada:
    """Agrega la alerta PENDIENTE a la transacción en curso (no hace commit)."""
    alerta = AlertaEnviada(evento_id=uuid.uuid4(), producto_id=producto_id, movimiento_id=movimiento_id,
                           saldo=saldo, umbral=umbral, estado="PENDIENTE", intentos=0)
    db.session.add(alerta)
    return alerta


def evento(alerta: AlertaEnviada) -> dict:
    producto, proveedor = db.session.execute(
        db.select(Producto, Proveedor).join(Proveedor, Proveedor.id == Producto.proveedor_id)
        .where(Producto.id == alerta.producto_id)
    ).one()
    return {
        "evento_id": str(alerta.evento_id),
        "tipo": "STOCK_CRITICO",
        "ocurrido_en": alerta.creado_en.isoformat(timespec="seconds"),
        "origen_datos": current_app.config["ORIGEN_DATOS"],
        "producto": {
            "sku": producto.sku,
            "nombre": producto.nombre,
            "saldo": alerta.saldo,
            "umbral": alerta.umbral,
            "plazo_entrega_dias": proveedor.plazo_entrega_dias,
        },
    }


def enviar(alerta_id: int) -> AlertaEnviada:
    """Envía una alerta y guarda el resultado (hace commit). Nunca lanza excepción."""
    alerta = db.session.get(AlertaEnviada, alerta_id, with_for_update=True)
    if alerta is None or alerta.estado == "ENVIADA":
        db.session.rollback()
        return alerta

    url = current_app.config.get("N8N_WEBHOOK_URL") or ""
    token = current_app.config.get("N8N_WEBHOOK_TOKEN") or ""
    error = None
    try:
        if not url or not token:
            error = "Webhook de n8n sin configurar (N8N_WEBHOOK_URL / N8N_WEBHOOK_TOKEN)"
        else:
            r = requests.post(url, json=evento(alerta), headers={"X-Demanda360-Token": token},
                              timeout=current_app.config["N8N_TIMEOUT_SEGUNDOS"])
            try:
                cuerpo = r.json()
            except ValueError:
                cuerpo = {}
            if r.status_code != 200 or not isinstance(cuerpo, dict) or cuerpo.get("ok") is not True:
                detalle = cuerpo.get("error") if isinstance(cuerpo, dict) else None
                error = f"n8n respondió {r.status_code}" + (f": {detalle}" if detalle else "")
    except requests.Timeout:
        error = "n8n no respondió a tiempo"
    except requests.RequestException as e:
        error = f"No se pudo conectar con n8n ({type(e).__name__})"

    alerta.intentos += 1
    if error is None:
        alerta.estado = "ENVIADA"
        alerta.enviado_en = datetime.now(timezone.utc)
        alerta.ultimo_error = None
    else:
        alerta.estado = "FALLIDA"
        alerta.ultimo_error = error[:200]
        log.warning("Alerta %s FALLIDA (intento %s): %s", alerta.evento_id, alerta.intentos, error)
    db.session.commit()
    return alerta


def pendientes_de_reintento() -> list[int]:
    """FALLIDAS con intentos disponibles, y PENDIENTES de hace más de un minuto
    (la app se cayó entre el commit de la venta y el envío)."""
    return list(db.session.execute(text("""
        SELECT id FROM alertas_enviadas
        WHERE intentos < :maximo
          AND (estado = 'FALLIDA' OR (estado = 'PENDIENTE' AND creado_en < now() - interval '1 minute'))
        ORDER BY creado_en
    """), {"maximo": MAX_INTENTOS}).scalars())
