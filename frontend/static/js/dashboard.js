/* ==========================================================================
   Demanda360 · pantalla Dashboard (diseño y lógica: Rol 4; integración: Rol 1)
   Requiere: api.js y comun.js. Lee GET /api/dashboard.
   Los KPI son del periodo de corte; el saldo de las tablas es el de hoy.
   ========================================================================== */

// { desde, hasta } → "1–30 sep 2026" (o "28 ago – 3 sep 2026" si cambia el mes)
function textoPeriodo(periodo) {
  if (!periodo || !periodo.desde || !periodo.hasta) return "";
  const i = partesFecha(periodo.desde), f = partesFecha(periodo.hasta);
  if (i.a === f.a && i.m === f.m) return `${i.d}–${f.d} ${f.m} ${f.a}`;
  if (i.a === f.a) return `${i.d} ${i.m} – ${f.d} ${f.m} ${f.a}`;
  return `${i.d} ${i.m} ${i.a} – ${f.d} ${f.m} ${f.a}`;
}

const formatoValor = new Intl.NumberFormat("es-CO", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

function fila(celdas, estado) {
  const tr = document.createElement("tr");
  celdas.forEach((valor) => tr.appendChild(el("td", null, valor)));
  const td = document.createElement("td");
  td.appendChild(etiquetaEstado(estado));
  tr.appendChild(td);
  return tr;
}

function filaVacia(tbody, columnas, mensaje) {
  const tr = document.createElement("tr");
  const td = el("td", "nota", mensaje);
  td.colSpan = columnas;
  tr.appendChild(td);
  tbody.appendChild(tr);
}

function pintarKpis(kpis) {
  const cont = document.getElementById("kpis");
  cont.replaceChildren();
  (kpis || []).forEach((k) => {
    const tarjeta = el("article", "tarjeta");
    tarjeta.dataset.kpi = k.codigo;
    tarjeta.appendChild(el("div", "subtitulo", k.nombre));
    const valor = typeof k.valor === "number" ? formatoValor.format(k.valor) : "—";
    tarjeta.appendChild(el("div", "kpi-valor", `${valor} ${k.unidad || ""}`.trim()));
    if (k.detalle) tarjeta.appendChild(el("div", null, k.detalle));
    if (k.meta) tarjeta.appendChild(el("div", "nota", "Meta: " + k.meta));
    cont.appendChild(tarjeta);
  });
}

function pintarCriticos(criticos) {
  const tbody = document.getElementById("tabla-criticos");
  tbody.replaceChildren();
  if (!criticos || criticos.length === 0) return filaVacia(tbody, 6, "No hay productos críticos ni agotados.");
  criticos.forEach((p) => tbody.appendChild(
    fila([p.sku, p.nombre, textoSaldo(p.saldo), p.umbral_reposicion, p.plazo_entrega_dias], p.estado)
  ));
}

function pintarInventario(inventario) {
  const tbody = document.getElementById("tabla-inventario");
  tbody.replaceChildren();
  if (!inventario || inventario.length === 0) return filaVacia(tbody, 7, "No hay productos registrados.");
  inventario.forEach((p) => tbody.appendChild(
    fila([p.sku, p.nombre, textoSaldo(p.saldo), p.vendidas_30d, p.no_atendidas_30d, p.plazo_entrega_dias], p.estado)
  ));
}

function mostrarError(mensaje) {
  const caja = document.getElementById("error");
  caja.textContent = mensaje || "No se pudo cargar el dashboard.";
  caja.hidden = false;
  document.getElementById("subtitulo").textContent = "Inventario y demanda";
}

async function cargarDashboard() {
  let r;
  try {
    r = await apiGet("/api/dashboard");
  } catch (e) {
    return mostrarError("No se pudo leer la respuesta del servidor.");
  }
  if (!r.ok) return mostrarError(r.error && r.error.mensaje);

  const d = r.data || {};
  const partes = ["Inventario y demanda"];
  if (Array.isArray(d.inventario)) partes.push(`${d.inventario.length} referencias`);
  document.getElementById("subtitulo").textContent = partes.join(" · ");

  const periodo = textoPeriodo(d.periodo);
  const notaKpis = [];
  if (periodo) notaKpis.push("Indicadores del periodo " + periodo);
  if (d.corte) { const c = partesFecha(d.corte); notaKpis.push(`fecha de corte: ${c.d} ${c.m} ${c.a}`); }
  document.getElementById("nota-kpis").textContent = notaKpis.join(" · ");
  marcarOrigenDatos(d.origen_datos);

  pintarKpis(d.kpis);
  pintarCriticos(d.criticos);
  pintarInventario(d.inventario);
}

cargarDashboard();
