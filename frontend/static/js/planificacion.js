/* ==========================================================================
   Demanda360 · pantalla Planificación de pedidos (P1)
   Requiere: api.js y comun.js. Basada en el Figma (planificacion_pedidos.png).
   - Propietario: cantidades sugeridas (GET /api/sugeridos), guardar borrador
     (POST /api/pedidos, uno por proveedor) y avanzar cada pedido
     (aprobar, enviar, confirmar, cancelar con reintento a otro proveedor).
   - Trabajador: ve la lista de pedidos.
   La sugerida y las transiciones las decide el backend; aquí solo se muestran.
   ========================================================================== */

const ESTADOS_PEDIDO = {
  BORRADOR:   { texto: "Borrador",   clase: "etiqueta-normal" },
  APROBADO:   { texto: "Aprobado",   clase: "etiqueta-simulado" },
  ENVIADO:    { texto: "Enviado",    clase: "etiqueta-critico" },
  CONFIRMADO: { texto: "Confirmado", clase: "etiqueta-confirmado" },
  CANCELADO:  { texto: "Cancelado",  clase: "etiqueta-agotado" },
};

const decimal2 = new Intl.NumberFormat("es-CO", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const decimal1 = new Intl.NumberFormat("es-CO", { maximumFractionDigits: 1 });

let sugeridos = [];
let proveedores = [];

function esPropietario() { return document.body.dataset.rol === "propietario"; }

function etiquetaPedido(estado) {
  const e = ESTADOS_PEDIDO[estado] || { texto: estado, clase: "etiqueta-normal" };
  return el("span", "etiqueta " + e.clase, e.texto);
}

function mostrarAviso(id, mensaje, tipo) {
  const caja = document.getElementById(id);
  caja.className = "alerta " + (tipo === "ok" ? "alerta-ok" : "alerta-error");
  caja.textContent = mensaje;
  caja.hidden = !mensaje;
}

/* ---------- Cantidades sugeridas ---------- */
function totalEnBorrador() {
  return [...document.querySelectorAll("#tabla-sugeridos input[data-producto]")]
    .reduce((suma, i) => suma + (/^\d+$/.test(i.value.trim()) ? Number(i.value) : 0), 0);
}

function pintarResumen(d) {
  document.getElementById("res-prioritarias").textContent = d.referencias_prioritarias;
  document.getElementById("res-total-sugerido").textContent = `${d.total_sugerido} unidades`;
  document.getElementById("res-total-borrador").textContent = `${totalEnBorrador()} unidades`;
}

function pintarSugeridos(d) {
  const tbody = document.getElementById("tabla-sugeridos");
  tbody.replaceChildren();
  sugeridos = d.productos || [];
  sugeridos.forEach((p) => {
    const tr = document.createElement("tr");
    tr.appendChild(el("td", null, `${p.sku} · ${p.nombre}`));
    tr.appendChild(el("td", null, textoSaldo(p.saldo)));
    tr.appendChild(el("td", null, p.demanda_diaria === null ? "—" : decimal2.format(p.demanda_diaria)));
    tr.appendChild(el("td", null, `${p.plazo_entrega_dias} días`));
    const sug = el("td", "sugerido", p.sugerido === null ? "Datos insuficientes" : p.sugerido);
    sug.title = p.formula;   // la explicación de cada número (regla versión 1)
    tr.appendChild(sug);
    const tdInput = document.createElement("td");
    const input = document.createElement("input");
    input.type = "number"; input.min = "0"; input.step = "1"; input.inputMode = "numeric";
    input.value = p.sugerido === null ? 0 : p.sugerido;
    input.dataset.producto = String(p.id);
    input.setAttribute("aria-label", `Cantidad a pedir de ${p.sku}`);
    input.addEventListener("input", () => pintarResumen(d));
    tdInput.appendChild(input);
    tr.appendChild(tdInput);
    tbody.appendChild(tr);
  });
  document.getElementById("regla").textContent = d.regla;
  const ejemplos = document.getElementById("formulas");
  ejemplos.replaceChildren();
  sugeridos.filter((p) => p.sugerido !== 0).forEach((p) => ejemplos.appendChild(el("li", null, `${p.sku}: ${p.formula}`)));
  document.getElementById("subtitulo").textContent =
    `Cantidades sugeridas · periodo hasta ${partesFecha(d.corte).d} ${partesFecha(d.corte).m} ${partesFecha(d.corte).a} · cobertura ${d.cobertura_dias} días`;
  marcarOrigenDatos(d.origen_datos);
  pintarResumen(d);
}

async function cargarSugeridos() {
  const cobertura = document.getElementById("cobertura").value.trim();
  if (!/^\d+$/.test(cobertura) || Number(cobertura) < 1 || Number(cobertura) > 90) {
    return mostrarAviso("aviso-sugeridos", "La cobertura debe ser un entero entre 1 y 90 días.");
  }
  mostrarAviso("aviso-sugeridos", "");
  const r = await apiGet(`/api/sugeridos?cobertura=${cobertura}`);
  if (!r.ok) return mostrarAviso("aviso-sugeridos", (r.error && r.error.mensaje) || "No se pudieron calcular las cantidades.");
  pintarSugeridos(r.data);
}

/** Guarda un borrador por proveedor habitual con las cantidades > 0. No compra ni mueve inventario. */
async function guardarBorradores() {
  const boton = document.getElementById("guardar-borrador");
  const lineas = [...document.querySelectorAll("#tabla-sugeridos input[data-producto]")];
  const invalidas = lineas.filter((i) => !/^\d+$/.test(i.value.trim()));
  lineas.forEach((i) => i.classList.toggle("campo-error", invalidas.includes(i)));
  if (invalidas.length) return mostrarAviso("aviso-borrador", "Las cantidades deben ser enteros de 0 o más.");

  const porProveedor = new Map();
  lineas.forEach((i) => {
    const cantidad = Number(i.value);
    if (cantidad === 0) return;
    const p = sugeridos.find((s) => String(s.id) === i.dataset.producto);
    if (!porProveedor.has(p.proveedor_id)) porProveedor.set(p.proveedor_id, { nombre: p.proveedor, detalles: [] });
    porProveedor.get(p.proveedor_id).detalles.push({ producto_id: p.id, cantidad_solicitada: cantidad });
  });
  if (porProveedor.size === 0) return mostrarAviso("aviso-borrador", "No hay cantidades para pedir.");

  boton.disabled = true;
  const creados = [], errores = [];
  for (const [proveedorId, grupo] of porProveedor) {
    const r = await apiPost("/api/pedidos", {
      proveedor_id: proveedorId,
      cobertura_dias: Number(document.getElementById("cobertura").value),
      detalles: grupo.detalles,
    });
    if (r.ok) creados.push(`n.º ${r.data.id} (${grupo.nombre})`);
    else errores.push(`${grupo.nombre}: ${(r.error && r.error.mensaje) || "error"}`);
  }
  boton.disabled = false;
  if (errores.length) mostrarAviso("aviso-borrador", "No se guardó: " + errores.join(" · "));
  else mostrarAviso("aviso-borrador", `Borradores guardados: ${creados.join(", ")}. Quedan pendientes de aprobación.`, "ok");
  cargarPedidos();
}

/* ---------- Pedidos ---------- */
function textoFechas(p) {
  const partes = [["Creado", p.fecha_creacion], ["Aprobado", p.fecha_aprobacion], ["Enviado", p.fecha_envio],
                  ["Respuesta", p.fecha_respuesta]]
    .filter(([, f]) => f).map(([t, f]) => `${t}: ${textoFecha(f)}`);
  if (p.fecha_entrega_estimada) {
    const e = partesFecha(p.fecha_entrega_estimada);
    partes.push(`Entrega estimada: ${e.d} ${e.m} ${e.a}`);
  }
  return partes;
}

function botonAccion(texto, alClic, primario) {
  const b = el("button", "boton" + (primario ? " boton-primario" : ""), texto);
  b.type = "button";
  b.addEventListener("click", alClic);
  return b;
}

async function accion(pedido, ruta, cuerpo, boton) {
  boton.disabled = true;
  const r = await apiPost(ruta, cuerpo);
  boton.disabled = false;
  if (!r.ok) return mostrarAviso("aviso-pedidos", `Pedido ${pedido.id}: ${(r.error && r.error.mensaje) || "error"}`);
  const extra = r.data.reintento ? ` Se creó el reintento n.º ${r.data.reintento.id} (aprobado).` : "";
  mostrarAviso("aviso-pedidos", `Pedido ${pedido.id}: ${ESTADOS_PEDIDO[r.data.estado].texto.toLowerCase()}.${extra}`, "ok");
  cargarPedidos();
}

function formularioCancelar(pedido, celda) {
  const form = el("form", "cancelar");
  const motivo = document.createElement("input");
  motivo.placeholder = "Motivo (obligatorio)"; motivo.maxLength = 300;
  motivo.setAttribute("aria-label", `Motivo de cancelación del pedido ${pedido.id}`);
  const otro = document.createElement("select");
  otro.setAttribute("aria-label", "Reintentar con otro proveedor");
  otro.appendChild(el("option", null, "Sin reintento"));
  otro.firstChild.value = "";
  proveedores.filter((pr) => pr.id !== pedido.proveedor_id).forEach((pr) => {
    const op = el("option", null, `Reintentar con ${pr.nombre}`);
    op.value = String(pr.id);
    otro.appendChild(op);
  });
  const enviar = el("button", "boton boton-peligro", "Confirmar cancelación");
  enviar.type = "submit";
  form.append(motivo, otro, enviar);
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (motivo.value.trim().length < 5) { motivo.classList.add("campo-error"); motivo.focus(); return; }
    accion(pedido, `/api/pedidos/${pedido.id}/estado`, {
      estado: "CANCELADO",
      motivo_cancelacion: motivo.value.trim(),
      reintentar_con_proveedor_id: otro.value ? Number(otro.value) : null,
    }, enviar);
  });
  celda.replaceChildren(form);
  motivo.focus();
}

function accionesDe(p, celda) {
  const cont = el("div", "acciones-pedido");
  const estado = (destino, texto, primario) => botonAccion(texto, (e) =>
    accion(p, `/api/pedidos/${p.id}/estado`, { estado: destino }, e.target), primario);
  if (p.estado === "BORRADOR") cont.appendChild(botonAccion("Aprobar", (e) => accion(p, `/api/pedidos/${p.id}/aprobar`, {}, e.target), true));
  if (p.estado === "APROBADO") cont.appendChild(estado("ENVIADO", "Marcar enviado", true));
  if (p.estado === "ENVIADO") cont.appendChild(estado("CONFIRMADO", "Proveedor confirmó", true));
  if (["BORRADOR", "APROBADO", "ENVIADO"].includes(p.estado)) {
    cont.appendChild(botonAccion("Cancelar…", () => formularioCancelar(p, celda)));
  }
  return cont;
}

function pintarPedidos(pedidos) {
  const tbody = document.getElementById("tabla-pedidos");
  tbody.replaceChildren();
  if (!pedidos.length) {
    const td = el("td", "nota", "Todavía no hay pedidos.");
    td.colSpan = 6;
    tbody.appendChild(document.createElement("tr")).appendChild(td);
    return;
  }
  pedidos.forEach((p) => {
    const tr = document.createElement("tr");
    tr.dataset.pedido = String(p.id);
    tr.appendChild(el("td", null, p.id));
    const prov = el("td", null, p.proveedor);
    if (p.numero_intento > 1) prov.appendChild(el("div", "nota", `Intento ${p.numero_intento} (reintento del n.º ${p.pedido_anterior_id})`));
    tr.appendChild(prov);
    const tdEstado = document.createElement("td");
    tdEstado.appendChild(etiquetaPedido(p.estado));
    if (p.horas_esperando !== null && p.horas_esperando !== undefined) {
      tdEstado.appendChild(el("div", "nota", `Esperando respuesta: ${decimal1.format(p.horas_esperando)} h`));
    }
    if (p.motivo_cancelacion) tdEstado.appendChild(el("div", "nota", `Motivo: ${p.motivo_cancelacion}`));
    if (p.reintento_id) tdEstado.appendChild(el("div", "nota", `Reintentado en el n.º ${p.reintento_id}`));
    tr.appendChild(tdEstado);
    const tdDetalle = document.createElement("td");
    p.detalles.forEach((d) => tdDetalle.appendChild(el("div", null,
      `${d.sku} × ${d.cantidad_solicitada}` + (d.cantidad_sugerida === null ? " (manual)" : ` (sugerido ${d.cantidad_sugerida})`))));
    tr.appendChild(tdDetalle);
    const tdFechas = document.createElement("td");
    textoFechas(p).forEach((t) => tdFechas.appendChild(el("div", "nota", t)));
    tr.appendChild(tdFechas);
    const tdAcciones = document.createElement("td");
    if (esPropietario()) tdAcciones.appendChild(accionesDe(p, tdAcciones));
    tr.appendChild(tdAcciones);
    tbody.appendChild(tr);
  });
}

async function cargarPedidos() {
  const r = await apiGet("/api/pedidos");
  if (!r.ok) return mostrarAviso("aviso-pedidos", (r.error && r.error.mensaje) || "No se pudieron cargar los pedidos.");
  marcarOrigenDatos(r.data.origen_datos);
  pintarPedidos(r.data.pedidos || []);
}

async function cargarProveedores() {
  const r = await apiGet("/api/catalogos");
  if (r.ok) proveedores = r.data.proveedores || [];
}

/* ---------- Inicio ---------- */
document.getElementById("recalcular").addEventListener("click", cargarSugeridos);
document.getElementById("cobertura").addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); cargarSugeridos(); } });
document.getElementById("guardar-borrador").addEventListener("click", guardarBorradores);
const avisoMock = document.getElementById("aviso-mock");
if (avisoMock) avisoMock.hidden = !USE_MOCK;

(async () => {
  if (esPropietario()) {
    await cargarProveedores();
    cargarSugeridos();
  } else {
    document.getElementById("subtitulo").textContent = "Pedidos a proveedores";
  }
  cargarPedidos();
})();
