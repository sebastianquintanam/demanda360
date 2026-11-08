"""Modelos SQLAlchemy mapeados a las tablas de database/sql/01_schema.sql.

No se usa create_all ni migraciones: si cambia el esquema, se cambia el SQL
(por PR) y luego este mapeo. La prueba tests/test_esquema.py compara ambos.
"""

from .catalogo import Categoria, Producto, Proveedor
from .inventario import ConteoFisico, Movimiento, SolicitudCliente
from .pedidos import Pedido, PedidoDetalle
from .registro import AlertaEnviada, Auditoria
from .usuario import Usuario

__all__ = [
    "AlertaEnviada",
    "Auditoria",
    "Categoria",
    "ConteoFisico",
    "Movimiento",
    "Pedido",
    "PedidoDetalle",
    "Producto",
    "Proveedor",
    "SolicitudCliente",
    "Usuario",
]
