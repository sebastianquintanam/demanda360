"""El esquema SQL es la fuente de verdad: estas pruebas verifican que el mapeo
de SQLAlchemy coincide y que la base protege las reglas aunque falle el backend."""

import pytest
from sqlalchemy import exc, inspect, text

from app.extensions import db as _db


def test_modelos_coinciden_con_las_tablas(db):
    inspector = inspect(db.engine)
    tablas_bd = set(inspector.get_table_names())
    for mapper in _db.Model.registry.mappers:
        tabla = mapper.local_table
        assert tabla.name in tablas_bd, f"Falta la tabla {tabla.name} en 01_schema.sql"
        cols_bd = {c["name"]: c for c in inspector.get_columns(tabla.name)}
        cols_orm = {c.name: c for c in tabla.columns}
        assert set(cols_orm) == set(cols_bd), f"Columnas distintas en {tabla.name}"
        for nombre, col in cols_orm.items():
            if not col.primary_key:
                assert col.nullable == cols_bd[nombre]["nullable"], f"{tabla.name}.{nombre}: nullable distinto"
    assert len(tablas_bd) == 11


def _datos_base(db):
    db.session.execute(text("""
        INSERT INTO usuarios (nombre, usuario, password_hash, rol) VALUES ('P', 'prop', 'x', 'propietario');
        INSERT INTO categorias (nombre) VALUES ('Lacas');
        INSERT INTO proveedores (codigo, nombre, plazo_entrega_dias) VALUES ('PRV-AND', 'Andinos (ficticio)', 3);
        INSERT INTO productos (sku, nombre, categoria_id, proveedor_id, presentacion, unidad_medida,
                               costo_compra, precio_venta, umbral_reposicion)
        VALUES ('LAC-BP-01', 'Laca alto brillo galón', 1, 1, 'Galón', 'galon', 85000, 110000, 5);
    """))
    db.session.commit()


def _falla(db, sql):
    with pytest.raises(exc.DBAPIError):
        db.session.execute(text(sql))
    db.session.rollback()


def test_sku_duplicado_o_en_minusculas_rechazado(db):
    _datos_base(db)
    base = ("INSERT INTO productos (sku, nombre, categoria_id, proveedor_id, presentacion, unidad_medida,"
            " costo_compra, precio_venta, umbral_reposicion) VALUES ('{}', 'X', 1, 1, 'Galón', 'galon', 1, 1, 1)")
    _falla(db, base.format("LAC-BP-01"))
    _falla(db, base.format("lac-bp-09"))


def test_categoria_sin_distinguir_mayusculas(db):
    _datos_base(db)
    _falla(db, "INSERT INTO categorias (nombre) VALUES (' LACAS ')")


def test_ajuste_sin_justificacion_rechazado(db):
    _datos_base(db)
    _falla(db, "INSERT INTO movimientos (producto_id, tipo, cantidad, usuario_id, origen_ref)"
               " VALUES (1, 'AJUSTE', -2, 1, 'r1')")
    _falla(db, "INSERT INTO movimientos (producto_id, tipo, cantidad, usuario_id, origen_ref)"
               " VALUES (1, 'VENTA', 0, 1, 'r2')")


def test_entregada_mayor_que_solicitada_rechazada(db):
    _datos_base(db)
    _falla(db, "INSERT INTO solicitudes_clientes (producto_id, cantidad_solicitada, cantidad_entregada,"
               " usuario_id, origen_ref) VALUES (1, 2, 3, 1, 's1')")


def test_entrega_sin_venta_rechazada(db):
    _datos_base(db)
    _falla(db, "INSERT INTO solicitudes_clientes (producto_id, cantidad_solicitada, cantidad_entregada,"
               " usuario_id, origen_ref) VALUES (1, 2, 2, 1, 's1')")


@pytest.mark.parametrize("tabla", ["movimientos", "auditoria"])
def test_tablas_de_solo_insercion(db, tabla):
    _datos_base(db)
    db.session.execute(text(
        "INSERT INTO movimientos (producto_id, tipo, cantidad, usuario_id, origen_ref) VALUES (1, 'ENTRADA', 5, 1, 'e1');"
        "INSERT INTO auditoria (usuario_id, accion, entidad) VALUES (1, 'PRUEBA', 'x');"
    ))
    db.session.commit()
    _falla(db, f"UPDATE {tabla} SET id = id")
    _falla(db, f"DELETE FROM {tabla}")


def test_pedido_aprobado_exige_aprobador(db):
    _datos_base(db)
    _falla(db, "INSERT INTO pedidos (proveedor_id, estado, creado_por) VALUES (1, 'APROBADO', 1)")


def test_zona_horaria_bogota(db):
    assert db.session.execute(text("SHOW timezone")).scalar() == "America/Bogota"
