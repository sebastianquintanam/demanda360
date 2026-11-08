"""Genera database/seeds/10_demo.sql: 30 días SIMULADOS de septiembre de 2026.

    python3 database/seeds/generar_demo.py          # reescribe 10_demo.sql
    python3 database/seeds/generar_demo.py --check  # falla si 10_demo.sql no coincide

Reproduce las cifras del Figma con una semilla fija (mismo archivo en cada corrida):
  · 11 referencias, 4 proveedores ficticios (plazos de 3, 4, 5 y 7 días)
  · 127 unidades vendidas y 12 no atendidas de 139 solicitadas
  · KPI 1 = 27,3 % (3 de 11) · KPI 2 = 8,6 % · KPI 3 = 50 % (5 de 10; 1 con datos insuficientes)
  · Sugerido de la laca alto brillo = 24 y total sugerido = 54 (cobertura de 14 días)
  · Pedidos con fechas para los KPI 4 y 5, incluido un reintento con otro proveedor

Cómo se arma: para cada referencia se fija su existencia inicial, sus entradas y su
demanda total; luego se simulan las atenciones en orden y se entrega lo que alcance.
Si la simulación no deja exactamente las vendidas y no atendidas del Figma, se prueba
con la siguiente semilla de esa referencia (determinista). No hay ventas los domingos.

Todo es ficticio: nombres de proveedor, marcas, precios y fechas. No hay datos de clientes.
"""

from __future__ import annotations

import argparse
import random
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

SEMILLA = "demanda360-septiembre-2026"
SALIDA = Path(__file__).with_name("10_demo.sql")
ZONA = "-05"  # Bogotá no tiene horario de verano

CATEGORIAS = ("Lacas", "Esmaltes", "Selladores")

# codigo, nombre, plazo de entrega (días), contacto (opcional, se deja vacío)
PROVEEDORES = (
    ("SUM-AND", "Suministros Andinos (ficticio)", 3),
    ("DIS-COR", "Distribuidora Cordillera (ficticio)", 4),
    ("QUI-SAB", "Químicos La Sabana (ficticio)", 5),
    ("PIN-LLA", "Pinturas del Llano (ficticio)", 7),
)


@dataclass
class Ref:
    sku: str
    nombre: str
    categoria: str
    proveedor: str
    presentacion: str
    unidad: str
    costo: int
    precio: int
    umbral: int
    inicial: int                      # conteo inicial
    vendidas: int                     # objetivo del Figma
    no_atendidas: int                 # objetivo del Figma
    final: int                        # saldo y conteo del 30 de septiembre
    entradas: list = field(default_factory=list)   # [(datetime, cantidad)]
    ajustes: list = field(default_factory=list)    # [(datetime, cantidad, justificación)]
    primer_conteo: datetime = datetime(2026, 9, 1, 7, 30)
    max_por_atencion: int = 2


def dt(dia: int, hora: int, minuto: int = 0) -> datetime:
    return datetime(2026, 9, dia, hora, minuto)


# Orden = id esperado en una base nueva (coincide con frontend/static/mock/)
REFERENCIAS = (
    Ref("LAC-BP-01", "Laca catalizada alto brillo galón", "Lacas", "SUM-AND", "Galón", "galon",
        85000, 110000, 6, inicial=20, vendidas=45, no_atendidas=6, final=0,
        entradas=[(dt(7, 8, 15), 25)], max_por_atencion=3),
    Ref("LAC-BP-02", "Laca catalizada mate galón", "Lacas", "DIS-COR", "Galón", "galon",
        82000, 106000, 4, inicial=8, vendidas=18, no_atendidas=3, final=0,
        entradas=[(dt(14, 8, 15), 10)]),
    Ref("ESM-WH-01", "Esmalte blanco galón", "Esmaltes", "SUM-AND", "Galón", "galon",
        52000, 68000, 4, inicial=24, vendidas=24, no_atendidas=2, final=0),
    Ref("SEL-AQ-01", "Sellador acuático galón", "Selladores", "QUI-SAB", "Galón", "galon",
        47000, 62000, 6, inicial=12, vendidas=20, no_atendidas=1, final=5,
        entradas=[(dt(19, 8, 15), 13)]),
    Ref("SEL-CA-01", "Sellador catalizado 45 % galón", "Selladores", "QUI-SAB", "Galón", "galon",
        58000, 76000, 4, inicial=16, vendidas=12, no_atendidas=0, final=4),
    Ref("LAC-TR-01", "Laca transparente galón", "Lacas", "DIS-COR", "Galón", "galon",
        80000, 104000, 3, inicial=10, vendidas=2, no_atendidas=0, final=8,
        primer_conteo=dt(28, 10, 0), max_por_atencion=1),
    Ref("ESM-SI-01", "Esmalte sintético cuñete", "Esmaltes", "PIN-LLA", "Cuñete", "cunete",
        210000, 265000, 2, inicial=17, vendidas=2, no_atendidas=0, final=15, max_por_atencion=1),
    Ref("SEL-AC-01", "Sellador acrílico galón", "Selladores", "QUI-SAB", "Galón", "galon",
        45000, 59000, 3, inicial=13, vendidas=1, no_atendidas=0, final=12, max_por_atencion=1),
    Ref("LAC-NG-01", "Laca nogal galón", "Lacas", "DIS-COR", "Galón", "galon",
        78000, 101000, 3, inicial=10, vendidas=1, no_atendidas=0, final=9, max_por_atencion=1),
    Ref("ESM-RJ-01", "Esmalte rojo galón", "Esmaltes", "SUM-AND", "Galón", "galon",
        54000, 70000, 3, inicial=11, vendidas=0, no_atendidas=0, final=10,
        ajustes=[(dt(21, 9, 40), -1, "Galón con la tapa rota en bodega; se retira de la venta")]),
    Ref("SEL-MU-01", "Sellador para muros cuñete", "Selladores", "QUI-SAB", "Cuñete", "cunete",
        190000, 240000, 3, inicial=13, vendidas=2, no_atendidas=0, final=11, max_por_atencion=1),
)

CONTEO_FINAL = dt(30, 19, 0)

# Pedidos del mes. Fechas en hora de Bogotá. El reintento enlaza al pedido cancelado.
PEDIDOS = (
    {"clave": "A", "proveedor": "SUM-AND", "estado": "CONFIRMADO", "intento": 1, "anterior": None,
     "creado": dt(4, 9, 0), "aprobado": dt(4, 9, 15), "enviado": dt(4, 9, 30), "respuesta": dt(4, 12, 30),
     "entrega": date(2026, 9, 7), "motivo": None, "detalles": [("LAC-BP-01", 25, 25)]},
    {"clave": "B", "proveedor": "DIS-COR", "estado": "CANCELADO", "intento": 1, "anterior": None,
     "creado": dt(9, 10, 0), "aprobado": dt(9, 10, 10), "enviado": dt(9, 10, 20), "respuesta": None,
     "entrega": None, "motivo": "Sin respuesta del proveedor en 48 horas; se pide a otro proveedor",
     "detalles": [("LAC-BP-02", 10, 10)]},
    {"clave": "C", "proveedor": "SUM-AND", "estado": "CONFIRMADO", "intento": 2, "anterior": "B",
     "creado": dt(11, 10, 30), "aprobado": dt(11, 10, 40), "enviado": dt(11, 10, 45), "respuesta": dt(11, 16, 45),
     "entrega": date(2026, 9, 14), "motivo": None, "detalles": [("LAC-BP-02", 10, 10)]},
    {"clave": "D", "proveedor": "QUI-SAB", "estado": "CONFIRMADO", "intento": 1, "anterior": None,
     "creado": dt(14, 9, 0), "aprobado": dt(14, 9, 20), "enviado": dt(14, 9, 30), "respuesta": dt(14, 14, 30),
     "entrega": date(2026, 9, 19), "motivo": None, "detalles": [("SEL-AQ-01", 13, 13)]},
    {"clave": "E", "proveedor": "SUM-AND", "estado": "ENVIADO", "intento": 1, "anterior": None,
     "creado": dt(28, 9, 0), "aprobado": dt(28, 9, 10), "enviado": dt(28, 9, 20), "respuesta": None,
     "entrega": None, "motivo": None, "detalles": [("ESM-WH-01", 13, 13)]},
)


@dataclass
class Atencion:
    fecha: datetime
    sku: str
    solicitada: int
    entregada: int
    usuario: str


def dias_habiles(desde: datetime) -> list[date]:
    """Lunes a sábado desde el día dado hasta el 30 de septiembre (sin domingos)."""
    d = desde.date()
    dias = []
    while d <= date(2026, 9, 30):
        if d.weekday() != 6:
            dias.append(d)
        d += timedelta(days=1)
    return dias


def simular(ref: Ref) -> list[Atencion]:
    demanda_total = ref.vendidas + ref.no_atendidas
    if ref.inicial + sum(c for _, c in ref.entradas) + sum(c for _, c, _ in ref.ajustes) - ref.vendidas != ref.final:
        raise SystemExit(f"{ref.sku}: inicial + entradas + ajustes − vendidas ≠ final")

    for intento in range(10_000):
        rng = random.Random(f"{SEMILLA}|{ref.sku}|{intento}")
        # 1. Repartir la demanda total en atenciones de 1..max unidades
        cantidades, resto = [], demanda_total
        while resto > 0:
            q = min(resto, rng.randint(1, ref.max_por_atencion))
            cantidades.append(q)
            resto -= q
        # 2. Fecha y hora de cada atención (8:00 a 17:59, días hábiles después del primer conteo)
        dias = [d for d in dias_habiles(ref.primer_conteo) if d > ref.primer_conteo.date() or ref.primer_conteo.hour < 8]
        fechas = sorted(
            datetime.combine(rng.choice(dias), datetime.min.time()) + timedelta(hours=rng.randint(8, 17), minutes=rng.randint(0, 59))
            for _ in cantidades
        )
        # 3. Simular en orden con entradas y ajustes
        eventos = [(f, "ATN", q) for f, q in zip(fechas, cantidades)]
        eventos += [(f, "ENT", q) for f, q in ref.entradas]
        eventos += [(f, "AJU", q) for f, q, _ in ref.ajustes]
        eventos.sort(key=lambda e: (e[0], e[1] != "ENT"))  # a igual hora, primero la entrada
        saldo, atenciones = ref.inicial, []
        for f, tipo, q in eventos:
            if tipo == "ATN":
                entregada = min(q, saldo)
                saldo -= entregada
                usuario = "propietario" if rng.random() < 0.2 else "trabajador"
                atenciones.append(Atencion(f, ref.sku, q, entregada, usuario))
            else:
                saldo += q
        vendidas = sum(a.entregada for a in atenciones)
        if vendidas == ref.vendidas and demanda_total - vendidas == ref.no_atendidas and saldo == ref.final:
            return atenciones
    raise SystemExit(f"{ref.sku}: no se encontró una simulación que cuadre")


def ts(f: datetime) -> str:
    return f"'{f:%Y-%m-%d %H:%M:%S}{ZONA}'"


def txt(s: str | None) -> str:
    return "NULL" if s is None else "'" + s.replace("'", "''") + "'"


def generar() -> str:
    simulaciones = {ref.sku: simular(ref) for ref in REFERENCIAS}
    todas = sorted((a for lista in simulaciones.values() for a in lista), key=lambda a: (a.fecha, a.sku))

    vendidas = sum(a.entregada for a in todas)
    no_atendidas = sum(a.solicitada - a.entregada for a in todas)
    assert (vendidas, no_atendidas) == (127, 12), (vendidas, no_atendidas)

    L: list[str] = []
    w = L.append
    w("-- =============================================================================")
    w("-- Demanda360 · DATOS SIMULADOS de septiembre de 2026 (no son datos del negocio)")
    w("-- ARCHIVO GENERADO por database/seeds/generar_demo.py: no se edita a mano.")
    w(f"-- {len(todas)} atenciones · {vendidas} unidades vendidas · {no_atendidas} no atendidas · {len(PEDIDOS)} pedidos")
    w("-- Requisitos: base con 01_schema.sql y 02_vistas.sql, SIN productos, y con los")
    w("-- usuarios 'propietario' y 'trabajador' (flask crear-usuarios-demo).")
    w("-- Cargar: flask cargar-demo  (o psql -v ON_ERROR_STOP=1 -f database/seeds/10_demo.sql)")
    w("-- =============================================================================")
    w("")
    w("SET client_encoding = 'UTF8';")
    w("SET timezone = 'America/Bogota';")
    w("BEGIN;")
    w("")
    w("DO $$")
    w("BEGIN")
    w("  IF EXISTS (SELECT 1 FROM productos) OR EXISTS (SELECT 1 FROM movimientos) THEN")
    w("    RAISE EXCEPTION 'La base ya tiene productos o movimientos: los datos demo solo se cargan en una base vacía.';")
    w("  END IF;")
    w("  IF (SELECT count(*) FROM usuarios WHERE usuario IN ('propietario', 'trabajador')) <> 2 THEN")
    w("    RAISE EXCEPTION 'Faltan los usuarios propietario y trabajador: corre primero flask crear-usuarios-demo.';")
    w("  END IF;")
    w("END")
    w("$$;")
    w("")
    w("-- Ayudantes temporales (solo existen durante esta carga)")
    w("CREATE FUNCTION pg_temp.uid(p_usuario text) RETURNS bigint LANGUAGE sql STABLE AS")
    w("  $$ SELECT id FROM usuarios WHERE usuario = p_usuario $$;")
    w("CREATE FUNCTION pg_temp.pid(p_sku text) RETURNS bigint LANGUAGE sql STABLE AS")
    w("  $$ SELECT id FROM productos WHERE sku = p_sku $$;")
    w("CREATE FUNCTION pg_temp.atencion(p_ref text, p_sku text, p_solicitada int, p_entregada int,")
    w("                                 p_fecha timestamptz, p_usuario text) RETURNS void LANGUAGE plpgsql AS $$")
    w("DECLARE v_mov bigint;")
    w("BEGIN")
    w("  IF p_entregada > 0 THEN")
    w("    INSERT INTO movimientos (producto_id, tipo, cantidad, fecha_hora, usuario_id, origen_ref)")
    w("    VALUES (pg_temp.pid(p_sku), 'VENTA', p_entregada, p_fecha, pg_temp.uid(p_usuario), p_ref || '-VTA')")
    w("    RETURNING id INTO v_mov;")
    w("  END IF;")
    w("  INSERT INTO solicitudes_clientes (producto_id, cantidad_solicitada, cantidad_entregada, fecha_hora,")
    w("                                    usuario_id, movimiento_id, origen_ref)")
    w("  VALUES (pg_temp.pid(p_sku), p_solicitada, p_entregada, p_fecha, pg_temp.uid(p_usuario), v_mov, p_ref);")
    w("END $$;")
    w("")

    w("-- Catálogo -------------------------------------------------------------------")
    w("INSERT INTO categorias (nombre) VALUES " + ", ".join(f"({txt(c)})" for c in CATEGORIAS) + ";")
    w("INSERT INTO proveedores (codigo, nombre, plazo_entrega_dias) VALUES")
    w(",\n".join(f"  ({txt(c)}, {txt(n)}, {p})" for c, n, p in PROVEEDORES) + ";")
    w("INSERT INTO productos (sku, nombre, categoria_id, proveedor_id, marca, presentacion, unidad_medida,")
    w("                       costo_compra, precio_venta, umbral_reposicion, creado_en) VALUES")
    filas = []
    for r in REFERENCIAS:
        filas.append(
            f"  ({txt(r.sku)}, {txt(r.nombre)}, (SELECT id FROM categorias WHERE nombre = {txt(r.categoria)}), "
            f"(SELECT id FROM proveedores WHERE codigo = {txt(r.proveedor)}), 'ColorNova (ficticia)', "
            f"{txt(r.presentacion)}, {txt(r.unidad)}, {r.costo}, {r.precio}, {r.umbral}, {ts(r.primer_conteo - timedelta(minutes=30))})"
        )
    w(",\n".join(filas) + ";")
    w("")

    w("-- Conteos iniciales (la existencia inicial es un conteo) ----------------------")
    w("INSERT INTO conteos_fisicos (producto_id, cantidad_contada, fecha_hora, usuario_id, observaciones, origen_ref) VALUES")
    w(",\n".join(
        f"  (pg_temp.pid({txt(r.sku)}), {r.inicial}, {ts(r.primer_conteo)}, pg_temp.uid('propietario'), "
        f"{txt('Conteo inicial' if r.primer_conteo.day == 1 else 'Conteo inicial: referencia nueva en el catálogo')}, "
        f"{txt(f'DEMO-CNT-INI-{r.sku}')})"
        for r in REFERENCIAS
    ) + ";")
    w("")

    w("-- Pedidos (P1) y sus detalles ---------------------------------------------------")
    for p in PEDIDOS:
        anterior = (
            "NULL" if p["anterior"] is None
            else f"(SELECT id FROM pedidos WHERE fecha_creacion = {ts(next(x for x in PEDIDOS if x['clave'] == p['anterior'])['creado'])})"
        )
        w(
            "INSERT INTO pedidos (proveedor_id, estado, numero_intento, pedido_anterior_id, creado_por, aprobado_por,\n"
            "                     fecha_creacion, fecha_aprobacion, fecha_envio, fecha_respuesta, fecha_entrega_estimada, motivo_cancelacion)\n"
            f"VALUES ((SELECT id FROM proveedores WHERE codigo = {txt(p['proveedor'])}), {txt(p['estado'])}, {p['intento']}, {anterior},\n"
            f"        pg_temp.uid('trabajador'), pg_temp.uid('propietario'), {ts(p['creado'])}, {ts(p['aprobado'])},\n"
            f"        {ts(p['enviado'])}, {'NULL' if p['respuesta'] is None else ts(p['respuesta'])}, "
            f"{'NULL' if p['entrega'] is None else txt(p['entrega'].isoformat())}, {txt(p['motivo'])});"
        )
        for sku, sugerida, solicitada in p["detalles"]:
            w(
                "INSERT INTO pedido_detalles (pedido_id, producto_id, cantidad_sugerida, cantidad_solicitada)\n"
                f"VALUES ((SELECT id FROM pedidos WHERE fecha_creacion = {ts(p['creado'])}), pg_temp.pid({txt(sku)}), {sugerida}, {solicitada});"
            )
    w("")

    w("-- Entradas de mercancía y ajustes -------------------------------------------")
    for r in REFERENCIAS:
        for f, q in r.entradas:
            w("INSERT INTO movimientos (producto_id, tipo, cantidad, fecha_hora, usuario_id, origen_ref, justificacion) VALUES "
              f"(pg_temp.pid({txt(r.sku)}), 'ENTRADA', {q}, {ts(f)}, pg_temp.uid('propietario'), "
              f"{txt(f'DEMO-ENT-{f:%m%d}-{r.sku}')}, NULL);")
        for f, q, just in r.ajustes:
            w("INSERT INTO movimientos (producto_id, tipo, cantidad, fecha_hora, usuario_id, origen_ref, justificacion) VALUES "
              f"(pg_temp.pid({txt(r.sku)}), 'AJUSTE', {q}, {ts(f)}, pg_temp.uid('propietario'), "
              f"{txt(f'DEMO-AJU-{f:%m%d}-{r.sku}')}, {txt(just)});")
    w("")

    w(f"-- Atenciones a clientes ({len(todas)}): solicitado, entregado y la venta si hubo entrega")
    w("DO $do$")
    w("BEGIN")
    for i, a in enumerate(todas, start=1):
        w(f"  PERFORM pg_temp.atencion('DEMO-ATN-{i:04d}', {txt(a.sku)}, {a.solicitada}, {a.entregada}, {ts(a.fecha)}, {txt(a.usuario)});")
    w("END")
    w("$do$;")
    w("")

    w("-- Conteo de cierre del 30 de septiembre (coincide con el saldo calculado) ------")
    w("INSERT INTO conteos_fisicos (producto_id, cantidad_contada, fecha_hora, usuario_id, observaciones, origen_ref) VALUES")
    w(",\n".join(
        f"  (pg_temp.pid({txt(r.sku)}), {r.final}, {ts(CONTEO_FINAL)}, pg_temp.uid('propietario'), 'Conteo de cierre de mes', "
        f"{txt(f'DEMO-CNT-FIN-{r.sku}')})"
        for r in REFERENCIAS
    ) + ";")
    w("")

    w("-- Bitácora de la carga -----------------------------------------------------------")
    w("INSERT INTO auditoria (usuario_id, accion, entidad, entidad_id, detalle) VALUES")
    w(f"  (NULL, 'DATOS_DEMO_CARGADOS', 'sistema', NULL, '{{\"origen_datos\": \"SIMULADO\", \"periodo\": \"2026-09\", "
      f"\"referencias\": {len(REFERENCIAS)}, \"atenciones\": {len(todas)}, \"pedidos\": {len(PEDIDOS)}}}'::jsonb);")
    w("")
    w("-- Verificación: si algo no cuadra con el Figma, la carga completa se deshace")
    w("DO $$")
    w("DECLARE v record;")
    w("BEGIN")
    w("  FOR v IN SELECT codigo, valor FROM fn_kpi_resumen(DATE '2026-09-30') WHERE codigo IN ('KPI1', 'KPI2', 'KPI3') LOOP")
    w("    IF (v.codigo, v.valor) NOT IN (('KPI1', 27.3), ('KPI2', 8.6), ('KPI3', 50.0)) THEN")
    w("      RAISE EXCEPTION 'El % dio % y no la cifra del Figma', v.codigo, v.valor;")
    w("    END IF;")
    w("  END LOOP;")
    w("END")
    w("$$;")
    w("")
    w("COMMIT;")
    return "\n".join(L) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="solo verifica que 10_demo.sql esté al día")
    args = parser.parse_args()
    contenido = generar()
    if args.check:
        if not SALIDA.exists() or SALIDA.read_text(encoding="utf-8") != contenido:
            print("10_demo.sql no coincide con el generador: corre python3 database/seeds/generar_demo.py", file=sys.stderr)
            return 1
        print("10_demo.sql al día.")
        return 0
    SALIDA.write_text(contenido, encoding="utf-8")
    print(f"Escrito {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
