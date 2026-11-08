/* ==========================================================================
   Demanda360 · pantalla Registro (diseño y lógica: Rol 4; integración: Rol 1)
   Requiere: api.js y comun.js.
   Formularios: atención al cliente (POST /api/ventas), conteo (POST /api/conteos),
   entrada o ajuste (POST /api/movimientos) y crear producto (POST /api/productos).
   La pantalla solo valida el FORMATO; saldo, permisos y estados los decide el backend.
   ========================================================================== */

let productos = [];

/* ---------- Rol (solo visual; el backend responde 403 igual) ---------- */
function esPropietario() { return document.body.dataset.rol === "propietario"; }

function aplicarRol() {
  // Si el trabajador tenía "Ajuste" marcado, vuelve a "Entrada"
  if (!esPropietario()) {
    document.querySelector('#form-movimiento input[value="ENTRADA"]').checked = true;
  }
  actualizarTipoMovimiento();
}

// El rol viene de la sesión (Flask) o del selector «Ver como» del prototipo, antes de cargar este script.

/* ---------- Lista de productos (GET /api/productos) ---------- */
function pintarSaldo(select) {
  const cont = document.querySelector(`[data-saldo-de="${select.id}"]`);
  cont.replaceChildren();
  const p = productos.find((x) => String(x.id) === select.value);
  if (!p) return;
  cont.appendChild(el("span", "nota", "Saldo actual: " + textoSaldo(p.saldo)));
  cont.appendChild(etiquetaEstado(p.estado));
}

function llenarSelectores() {
  document.querySelectorAll(".selector-producto").forEach((select) => {
    const elegido = select.value;
    select.replaceChildren(el("option", null, "Selecciona un producto…"));
    select.firstChild.value = "";
    productos.forEach((p) => {
      const op = el("option", null, `${p.sku} · ${p.nombre}`);
      op.value = String(p.id);
      select.appendChild(op);
    });
    select.value = elegido;
    pintarSaldo(select);
  });
}

async function cargarProductos() {
  const caja = document.getElementById("error-productos");
  let r;
  try {
    r = await apiGet("/api/productos");
  } catch (e) {
    r = { ok: false, error: { mensaje: "No se pudo leer la lista de productos." } };
  }
  if (!r.ok) {
    caja.textContent = (r.error && r.error.mensaje) || "No se pudo cargar la lista de productos.";
    caja.hidden = false;
    return;
  }
  caja.hidden = true;
  productos = (r.data && r.data.productos) || [];
  marcarOrigenDatos(r.data && r.data.origen_datos);
  llenarSelectores();
}

document.querySelectorAll(".selector-producto").forEach((s) => s.addEventListener("change", () => pintarSaldo(s)));

/* ---------- Validación y errores de formulario ---------- */
const ENTERO = /^-?\d+$/;
const DINERO = /^\d+(\.\d{1,2})?$/;

function limpiarErrores(form) {
  form.querySelectorAll(".campo-error").forEach((c) => { c.classList.remove("campo-error"); c.removeAttribute("aria-invalid"); });
  form.querySelectorAll(".msg-campo").forEach((m) => m.remove());
  form.querySelectorAll("[data-ayuda]").forEach((a) => { a.hidden = false; });
  const caja = form.querySelector("[data-error]");
  caja.hidden = true;
  caja.textContent = "";
}

function marcarCampo(form, nombre, mensaje) {
  const campo = form.querySelector(`[name="${nombre}"]`);
  if (!campo) return false;
  campo.classList.add("campo-error");
  campo.setAttribute("aria-invalid", "true");
  if (mensaje) {
    // Si el campo tiene texto de ayuda, se oculta mientras se muestra el error (evita el mensaje duplicado)
    const ayuda = form.querySelector(`[data-ayuda="${nombre}"]`);
    if (ayuda) ayuda.hidden = true;
    campo.insertAdjacentElement("afterend", el("div", "msg-campo", mensaje));
  }
  return true;
}

function mostrarErrores(form, mensaje, campos) {
  const caja = form.querySelector("[data-error]");
  caja.textContent = mensaje || "Revisa los datos del formulario.";
  caja.hidden = false;
  Object.keys(campos || {}).forEach((nombre) => marcarCampo(form, nombre));
}

/** Lee un entero de un input o select. Devuelve null si está vacío o no es entero. */
function leerEntero(form, nombre) {
  const v = form.querySelector(`[name="${nombre}"]`).value.trim();
  return ENTERO.test(v) ? Number(v) : null;
}

function leerTexto(form, nombre) {
  const campo = form.querySelector(`[name="${nombre}"]`);
  return campo ? campo.value.trim() : "";
}

/* ---------- origen_ref: uno nuevo al abrir y tras cada registro exitoso ---------- */
const refs = {};
function renovarRef(form) {
  refs[form.id] = nuevoOrigenRef();
  const span = form.querySelector("[data-ref]");
  if (span) span.textContent = refs[form.id];
}

/* ---------- Resultado ---------- */
function listaDatos(filas) {
  const dl = document.createElement("dl");
  filas.forEach(([nombre, valor]) => {
    dl.appendChild(el("dt", null, nombre));
    const dd = document.createElement("dd");
    if (valor instanceof Node) dd.appendChild(valor); else dd.textContent = valor === null || valor === undefined ? "—" : String(valor);
    dl.appendChild(dd);
  });
  return dl;
}

function nombreProducto(id) {
  const p = productos.find((x) => x.id === id);
  return p ? `${p.sku} · ${p.nombre}` : id;
}

/** enviados = lo que el usuario escribió y se mandó a la API; filas = lo que respondió la API. */
function pintarResultado(form, titulo, filas, status, enviados) {
  const cont = form.parentElement.querySelector("[data-resultado]");
  cont.replaceChildren();
  const caja = el("div", "resultado");
  caja.appendChild(el("strong", null, status === 200 ? titulo + " (ya estaba registrado: reenvío)" : titulo));
  caja.appendChild(el("div", "subtitulo", "Datos enviados"));
  caja.appendChild(listaDatos(enviados || []));
  caja.appendChild(el("div", "subtitulo", USE_MOCK ? "Respuesta de la API (simulada)" : "Respuesta de la API"));
  if (USE_MOCK) {
    caja.appendChild(el("div", "nota",
      "No se guardó en la base de datos y es siempre el mismo ejemplo, " +
      "por eso puede no coincidir con los datos enviados."));
  }
  caja.appendChild(listaDatos(filas));
  cont.appendChild(caja);
}

function limpiarResultado(form) {
  form.parentElement.querySelector("[data-resultado]").replaceChildren();
}

/** Envía el formulario: bloquea el botón para evitar doble clic y procesa la respuesta. */
async function enviar(form, ruta, cuerpo, alExito) {
  const boton = form.querySelector('button[type="submit"]');
  boton.disabled = true;
  let r;
  try {
    r = await apiPost(ruta, cuerpo);
  } catch (e) {
    r = { ok: false, error: { mensaje: "No se pudo leer la respuesta del servidor.", campos: {} } };
  } finally {
    boton.disabled = false;
  }
  if (!r.ok) {
    // 400 VALIDACION, 403 SIN_PERMISO, 409 STOCK_INSUFICIENTE / SIN_CONTEO…: se muestra el mensaje del backend.
    // El origen_ref se conserva: si se corrige y reenvía, no se duplica.
    mostrarErrores(form, r.error && r.error.mensaje, r.error && r.error.campos);
    return;
  }
  form.dataset.conservarResultado = "1"; // el reset de abajo no debe borrar el resultado
  form.reset();
  alExito(r.data || {}, r.status, cuerpo);
  renovarRef(form);
  cargarProductos(); // con el backend real refresca el saldo; con mocks queda igual
}

/* ---------- 1. Atención al cliente ---------- */
const formVenta = document.getElementById("form-venta");
const chkRegreso = document.getElementById("venta-regreso");
const selPrevia = document.getElementById("venta-previa");
const notaPrevia = document.getElementById("venta-previa-nota");

/** Cliente que regresa: lista las atenciones del producto con faltante pendiente
    (GET /api/productos/{id} → faltantes_pendientes). No se escribe el número a mano. */
async function cargarFaltantes() {
  selPrevia.replaceChildren(el("option", null, "Selecciona la atención original…"));
  selPrevia.firstChild.value = "";
  notaPrevia.textContent = "";
  const productoId = leerEntero(formVenta, "producto_id");
  if (!chkRegreso.checked) return;
  if (productoId === null) { notaPrevia.textContent = "Primero elige el producto."; return; }
  const r = await apiGet(`/api/productos/${productoId}`);
  const faltantes = (r.ok && r.data && r.data.faltantes_pendientes) || [];
  if (faltantes.length === 0) {
    notaPrevia.textContent = r.ok
      ? "Este producto no tiene atenciones con faltante pendiente en los últimos 30 días."
      : "No se pudieron cargar las atenciones anteriores.";
    return;
  }
  faltantes.forEach((f) => {
    const op = el("option", null,
      `Atención n.º ${f.solicitud_id} · ${textoFecha(f.fecha_hora)} · faltan ${f.faltante_pendiente}`);
    op.value = String(f.solicitud_id);
    selPrevia.appendChild(op);
  });
  notaPrevia.textContent = "Esta venta no suma demanda nueva: completa lo que faltó en la atención original.";
}

chkRegreso.addEventListener("change", () => {
  document.getElementById("bloque-regreso").hidden = !chkRegreso.checked;
  cargarFaltantes();
});
document.getElementById("venta-producto").addEventListener("change", cargarFaltantes);

formVenta.addEventListener("submit", (e) => {
  e.preventDefault();
  limpiarErrores(formVenta);
  let ok = true;
  const productoId = leerEntero(formVenta, "producto_id");
  const solicitada = leerEntero(formVenta, "cantidad_solicitada");
  const entregada = leerEntero(formVenta, "cantidad_entregada");
  let previa = null;

  if (productoId === null) { marcarCampo(formVenta, "producto_id", "Elige un producto."); ok = false; }
  if (solicitada === null || solicitada < 1) { marcarCampo(formVenta, "cantidad_solicitada", "Entero mayor que 0."); ok = false; }
  if (entregada === null || entregada < 0) { marcarCampo(formVenta, "cantidad_entregada", "Entero de 0 o más."); ok = false; }
  else if (solicitada !== null && entregada > solicitada) { marcarCampo(formVenta, "cantidad_entregada", "No puede superar lo solicitado."); ok = false; }
  if (chkRegreso.checked) {
    previa = leerEntero(formVenta, "solicitud_previa_id");
    if (previa === null) { marcarCampo(formVenta, "solicitud_previa_id", "Elige la atención original."); ok = false; }
  }
  if (!ok) return mostrarErrores(formVenta, "Revisa los campos marcados.");

  enviar(formVenta, "/api/ventas", {
    producto_id: productoId,
    cantidad_solicitada: solicitada,
    cantidad_entregada: entregada,
    origen_ref: refs[formVenta.id],
    solicitud_previa_id: previa,
  }, (d, status, c) => {
    const p = d.producto || {};
    const enviados = [
      ["Producto", nombreProducto(c.producto_id)],
      ["Solicitada", c.cantidad_solicitada],
      ["Entregada", c.cantidad_entregada],
      ["Regreso de la atención n.º", c.solicitud_previa_id === null ? "No" : c.solicitud_previa_id],
      ["origen_ref", c.origen_ref],
    ];
    pintarResultado(formVenta, "Atención registrada", [
      ["Atención n.º", d.solicitud_id],
      ["Movimiento n.º", d.movimiento_id],
      ["Producto", p.sku],
      ["No atendidas", d.no_atendida],
      ["Saldo", `${textoSaldo(p.saldo_anterior)} → ${textoSaldo(p.saldo_actual)}`],
      ["Umbral", p.umbral_reposicion],
      ["Estado", etiquetaEstado(p.estado)],
      ["Alerta", d.alerta ? `${d.alerta.estado} (evento ${d.alerta.evento_id})` : "Sin alerta"],
    ], status, enviados);
    chkRegreso.checked = false;
    document.getElementById("bloque-regreso").hidden = true;
  });
});

/* ---------- 2. Conteo físico ---------- */
const formConteo = document.getElementById("form-conteo");
formConteo.addEventListener("submit", (e) => {
  e.preventDefault();
  limpiarErrores(formConteo);
  let ok = true;
  const productoId = leerEntero(formConteo, "producto_id");
  const contada = leerEntero(formConteo, "cantidad_contada");
  if (productoId === null) { marcarCampo(formConteo, "producto_id", "Elige un producto."); ok = false; }
  if (contada === null || contada < 0) { marcarCampo(formConteo, "cantidad_contada", "Entero de 0 o más."); ok = false; }
  if (!ok) return mostrarErrores(formConteo, "Revisa los campos marcados.");

  enviar(formConteo, "/api/conteos", {
    producto_id: productoId,
    cantidad_contada: contada,
    observaciones: leerTexto(formConteo, "observaciones") || null,
    origen_ref: refs[formConteo.id],
  }, (d, status, c) => {
    const p = d.producto || {};
    const enviados = [
      ["Producto", nombreProducto(c.producto_id)],
      ["Cantidad contada", c.cantidad_contada],
      ["origen_ref", c.origen_ref],
    ];
    pintarResultado(formConteo, "Conteo registrado", [
      ["Conteo n.º", d.id],
      ["Producto", p.sku],
      ["Cantidad contada", d.cantidad_contada],
      ["Fecha y hora", d.fecha_hora ? textoFecha(d.fecha_hora) : null],
      ["Saldo", `${textoSaldo(p.saldo_anterior)} → ${textoSaldo(p.saldo_actual)}`],
      ["Estado", etiquetaEstado(p.estado)],
    ], status, enviados);
  });
});

/* ---------- 3. Entrada o ajuste ---------- */
const formMov = document.getElementById("form-movimiento");
const MIN_JUSTIFICACION = 10;

function tipoMovimiento() {
  return formMov.querySelector('input[name="tipo"]:checked').value;
}

function actualizarTipoMovimiento() {
  const ajuste = tipoMovimiento() === "AJUSTE";
  document.getElementById("bloque-justificacion").hidden = !ajuste;
  document.getElementById("mov-cantidad-label").textContent = ajuste ? "Cantidad del ajuste" : "Cantidad recibida";
  document.getElementById("mov-cantidad-ayuda").textContent = ajuste
    ? "Entero distinto de 0: positivo suma, negativo resta (ej.: -2)."
    : "Entero mayor que 0.";
  document.getElementById("mov-cantidad").min = ajuste ? "" : "1";
}
formMov.querySelectorAll('input[name="tipo"]').forEach((r) => r.addEventListener("change", actualizarTipoMovimiento));

formMov.addEventListener("submit", (e) => {
  e.preventDefault();
  limpiarErrores(formMov);
  let ok = true;
  const tipo = tipoMovimiento();
  const productoId = leerEntero(formMov, "producto_id");
  const cantidad = leerEntero(formMov, "cantidad");
  const justificacion = leerTexto(formMov, "justificacion");

  if (productoId === null) { marcarCampo(formMov, "producto_id", "Elige un producto."); ok = false; }
  if (tipo === "ENTRADA" && (cantidad === null || cantidad < 1)) { marcarCampo(formMov, "cantidad", "Entero mayor que 0."); ok = false; }
  if (tipo === "AJUSTE") {
    if (cantidad === null || cantidad === 0) { marcarCampo(formMov, "cantidad", "Entero distinto de 0."); ok = false; }
    if (justificacion.length < MIN_JUSTIFICACION) {
      marcarCampo(formMov, "justificacion", `Explica el ajuste (mínimo ${MIN_JUSTIFICACION} caracteres).`); ok = false;
    }
  }
  if (!ok) return mostrarErrores(formMov, "Revisa los campos marcados.");

  enviar(formMov, "/api/movimientos", {
    producto_id: productoId,
    tipo: tipo,
    cantidad: cantidad,
    justificacion: tipo === "AJUSTE" ? justificacion : null,
    origen_ref: refs[formMov.id],
  }, (d, status, c) => {
    const p = d.producto || {};
    const enviados = [
      ["Producto", nombreProducto(c.producto_id)],
      ["Tipo", c.tipo],
      ["Cantidad", c.cantidad],
      ["Justificación", c.justificacion || "—"],
      ["origen_ref", c.origen_ref],
    ];
    pintarResultado(formMov, tipo === "AJUSTE" ? "Ajuste registrado" : "Entrada registrada", [
      ["Movimiento n.º", d.id],
      ["Tipo", d.tipo],
      ["Producto", p.sku],
      ["Cantidad", d.cantidad],
      ["Justificación", d.justificacion || "—"],
      ["Saldo", `${textoSaldo(p.saldo_anterior)} → ${textoSaldo(p.saldo_actual)}`],
      ["Estado", etiquetaEstado(p.estado)],
    ], status, enviados);
    actualizarTipoMovimiento();
  });
});

/* ---------- 4. Crear producto (solo propietario) ---------- */
const formProducto = document.getElementById("form-producto");

function llenarSelect(id, opciones, texto, vacio) {
  const select = document.getElementById(id);
  select.replaceChildren(el("option", null, vacio));
  select.firstChild.value = "";
  opciones.forEach((o) => {
    const op = el("option", null, texto(o));
    op.value = String(o.id !== undefined ? o.id : o);
    select.appendChild(op);
  });
}

const UNIDADES = { unidad: "Unidad", galon: "Galón", medio_galon: "Medio galón", cuarto_galon: "Cuarto de galón",
                   cunete: "Cuñete", litro: "Litro", kilogramo: "Kilogramo" };

async function cargarCatalogos() {
  if (!formProducto) return;
  const r = await apiGet("/api/catalogos");
  if (!r.ok) {
    mostrarErrores(formProducto, (r.error && r.error.mensaje) || "No se pudieron cargar categorías y proveedores.");
    return;
  }
  llenarSelect("p-categoria", r.data.categorias || [], (c) => c.nombre, "Selecciona…");
  llenarSelect("p-proveedor", r.data.proveedores || [], (p) => `${p.nombre} · entrega ${p.plazo_entrega_dias} d`, "Selecciona…");
  llenarSelect("p-unidad", r.data.unidades_medida || [], (u) => UNIDADES[u] || u, "Selecciona…");
}

if (formProducto) {
  formProducto.addEventListener("submit", (e) => {
    e.preventDefault();
    limpiarErrores(formProducto);
    let ok = true;
    const sku = leerTexto(formProducto, "sku").toUpperCase().replace(/\s+/g, "");
    const nombre = leerTexto(formProducto, "nombre");
    const categoria = leerEntero(formProducto, "categoria_id");
    const proveedor = leerEntero(formProducto, "proveedor_id");
    const unidad = leerTexto(formProducto, "unidad_medida");
    const presentacion = leerTexto(formProducto, "presentacion");
    const umbral = leerEntero(formProducto, "umbral_reposicion");
    const costo = leerTexto(formProducto, "costo_compra");
    const precio = leerTexto(formProducto, "precio_venta");

    if (!/^[A-Z0-9][A-Z0-9-]{2,29}$/.test(sku)) { marcarCampo(formProducto, "sku", "Letras, números y guiones (3 a 30)."); ok = false; }
    if (nombre.length < 3) { marcarCampo(formProducto, "nombre", "Mínimo 3 caracteres."); ok = false; }
    if (categoria === null) { marcarCampo(formProducto, "categoria_id", "Elige una categoría."); ok = false; }
    if (proveedor === null) { marcarCampo(formProducto, "proveedor_id", "Elige el proveedor habitual."); ok = false; }
    if (!unidad) { marcarCampo(formProducto, "unidad_medida", "Elige la unidad."); ok = false; }
    if (!presentacion) { marcarCampo(formProducto, "presentacion", "Ej.: Galón, Cuñete."); ok = false; }
    if (umbral === null || umbral < 0) { marcarCampo(formProducto, "umbral_reposicion", "Entero de 0 o más."); ok = false; }
    if (!DINERO.test(costo)) { marcarCampo(formProducto, "costo_compra", "Número ≥ 0, máximo 2 decimales."); ok = false; }
    if (!DINERO.test(precio)) { marcarCampo(formProducto, "precio_venta", "Número ≥ 0, máximo 2 decimales."); ok = false; }
    if (!ok) return mostrarErrores(formProducto, "Revisa los campos marcados.");

    const cuerpo = {
      sku, nombre, categoria_id: categoria, proveedor_id: proveedor,
      marca: leerTexto(formProducto, "marca") || null, presentacion, unidad_medida: unidad,
      costo_compra: Number(costo), precio_venta: Number(precio), umbral_reposicion: umbral,
    };
    enviar(formProducto, "/api/productos", cuerpo, (d, status, c) => {
      pintarResultado(formProducto, "Producto creado", [
        ["Producto n.º", d.id],
        ["SKU", d.sku],
        ["Nombre", d.nombre],
        ["Umbral", d.umbral_reposicion],
        ["Saldo", textoSaldo(d.saldo)],
        ["Estado", etiquetaEstado(d.estado)],
      ], status, [["SKU", c.sku], ["Nombre", c.nombre]]);
      const nota = el("p", "nota", "Siguiente paso: registra su conteo inicial en «Conteo físico».");
      formProducto.parentElement.querySelector("[data-resultado] .resultado").appendChild(nota);
    });
  });
}

/* ---------- «Limpiar»: borra campos y errores, mantiene el mismo origen_ref ---------- */
[formVenta, formConteo, formMov, formProducto].filter(Boolean).forEach((form) => {
  form.addEventListener("reset", () => {
    setTimeout(() => {
      limpiarErrores(form);
      if (form.dataset.conservarResultado) delete form.dataset.conservarResultado;
      else limpiarResultado(form);
      form.querySelectorAll(".selector-producto").forEach(pintarSaldo);
      if (form === formVenta) document.getElementById("bloque-regreso").hidden = true;
      if (form === formMov) actualizarTipoMovimiento();
    });
  });
});

/* ---------- Inicio ---------- */
const avisoMock = document.getElementById("aviso-mock");
if (avisoMock) avisoMock.hidden = !USE_MOCK;
[formVenta, formConteo, formMov].forEach(renovarRef);
aplicarRol();
cargarProductos();
if (esPropietario()) cargarCatalogos();
