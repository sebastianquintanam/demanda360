/* ==========================================================================
   Demanda360 · cliente de la API
   - USE_MOCK = true  → lee los archivos de /static/mock/ (sirve con Live Server
     abriendo la carpeta `frontend/` como raíz, sin Flask ni base de datos).
   - USE_MOCK = false → llama a la API real de Flask.
   Se decide solo: las páginas servidas por Flask traen <meta name="csrf-token">
   y usan la API real; los prototipos HTML no lo traen y usan los mocks.
   Para forzarlo, antes de este script: <script>window.USE_MOCK = true;</script>
   Las pantallas NO calculan reglas de negocio: solo muestran lo que llega.
   ========================================================================== */

const USE_MOCK = typeof window.USE_MOCK === "boolean"
  ? window.USE_MOCK
  : !document.querySelector('meta[name="csrf-token"]');

// Qué archivo de ejemplo responde cada ruta cuando USE_MOCK = true
const MOCKS = {
  "GET /api/health": "health.json",
  "GET /api/productos": "productos.json",
  "GET /api/productos/1": "producto_detalle.json",
  "GET /api/dashboard": "dashboard.json",
  "GET /api/analisis/rotacion": "rotacion.json",
  "GET /api/auditoria": "auditoria.json",
  "GET /api/sugeridos": "sugeridos.json",
  "GET /api/pedidos": "pedidos.json",
  "POST /api/productos": "producto_creado.json",
  "POST /api/conteos": "conteo_creado.json",
  "POST /api/ventas": "venta_creada.json",
  "POST /api/movimientos": "movimiento_creado.json",
  "POST /api/pedidos": "pedido_creado.json",
};

function csrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.content : "";
}

/** Genera el origen_ref del formulario (evita registros duplicados si se reenvía). */
function nuevoOrigenRef() {
  if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
  return "ref-" + Date.now() + "-" + Math.random().toString(16).slice(2);
}

/**
 * Llama a la API y devuelve siempre { ok, status, data, error }.
 * error = { codigo, mensaje, campos } con el formato del contrato.
 */
async function api(metodo, ruta, cuerpo) {
  const rutaSinQuery = ruta.split("?")[0];
  if (USE_MOCK) {
    const archivo = MOCKS[`${metodo} ${rutaSinQuery}`];
    if (!archivo) {
      return { ok: false, status: 404, data: null, error: { codigo: "SIN_MOCK", mensaje: `No hay mock para ${metodo} ${rutaSinQuery}`, campos: {} } };
    }
    const r = await fetch(`/static/mock/${archivo}`);
    const data = await r.json();
    return { ok: true, status: metodo === "POST" ? 201 : 200, data, error: null };
  }

  const opciones = { method: metodo, headers: { Accept: "application/json" }, credentials: "same-origin" };
  if (metodo !== "GET") {
    opciones.headers["Content-Type"] = "application/json";
    opciones.headers["X-CSRFToken"] = csrfToken();
    opciones.body = JSON.stringify(cuerpo || {});
  }

  let r;
  try {
    r = await fetch(ruta, opciones);
  } catch (e) {
    return { ok: false, status: 0, data: null, error: { codigo: "SIN_CONEXION", mensaje: "No hay conexión con el servidor.", campos: {} } };
  }

  if (r.status === 401) {
    window.location.href = "/login?next=" + encodeURIComponent(window.location.pathname);
    return { ok: false, status: 401, data: null, error: { codigo: "NO_AUTENTICADO", mensaje: "Debes iniciar sesión.", campos: {} } };
  }

  let data = null;
  try { data = await r.json(); } catch (e) { /* respuesta vacía */ }

  if (!r.ok) {
    const error = (data && data.error) || { codigo: "ERROR_INTERNO", mensaje: "Error inesperado.", campos: {} };
    return { ok: false, status: r.status, data: null, error };
  }
  return { ok: true, status: r.status, data, error: null };
}

const apiGet = (ruta) => api("GET", ruta);
const apiPost = (ruta, cuerpo) => api("POST", ruta, cuerpo);
