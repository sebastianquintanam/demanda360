/* ==========================================================================
   Demanda360 · utilidades comunes de las pantallas (Rol 4 + Rol 1)
   Lo usan los prototipos (con mocks) y las plantillas de Flask (API real):
   una sola copia del código. Las pantallas solo MUESTRAN lo que entrega la
   API; las reglas de negocio las decide el backend.
   Todo dato se inserta con textContent (nunca innerHTML).
   ========================================================================== */

// Los 6 estados del plan → texto y clase de estilos.css
const ESTADOS = {
  SIN_CONTEO:          { texto: "Sin conteo",          clase: "etiqueta-normal" },
  AGOTADO:             { texto: "Agotado",             clase: "etiqueta-agotado" },
  CRITICO:             { texto: "Crítico",             clase: "etiqueta-critico" },
  DATOS_INSUFICIENTES: { texto: "Datos insuficientes", clase: "etiqueta-datos-insuficientes" },
  BAJA_ROTACION:       { texto: "Baja rotación",       clase: "etiqueta-baja-rotacion" },
  NORMAL:              { texto: "Normal",              clase: "etiqueta-normal" },
};

const MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];

function el(etiqueta, clase, texto) {
  const nodo = document.createElement(etiqueta);
  if (clase) nodo.className = clase;
  if (texto !== undefined && texto !== null) nodo.textContent = String(texto);
  return nodo;
}

// Contrato: saldo null = el producto aún no tiene conteo. Nunca se muestra como 0.
function textoSaldo(saldo) {
  return saldo === null || saldo === undefined ? "Sin conteo" : saldo;
}

function etiquetaEstado(codigo) {
  const e = ESTADOS[codigo] || { texto: codigo || "—", clase: "etiqueta-normal" };
  return el("span", "etiqueta " + e.clase, e.texto);
}

// "2026-09-01" → { d: 1, m: "sep", a: 2026 } sin pasar por Date (evita desfase de zona horaria)
function partesFecha(iso) {
  const [a, m, d] = String(iso).split("-").map(Number);
  return { d, m: MESES[m - 1], a };
}

const _fechaHora = new Intl.DateTimeFormat("es-CO", { dateStyle: "medium", timeStyle: "short", timeZone: "America/Bogota" });
function textoFecha(iso) {
  const d = new Date(iso);
  return isNaN(d) ? iso : _fechaHora.format(d);
}

/** La etiqueta «Datos simulados» del encabezado sigue lo que diga la API. */
function marcarOrigenDatos(origen) {
  const etiqueta = document.getElementById("etiqueta-simulado");
  if (etiqueta) etiqueta.hidden = origen !== "SIMULADO";
}
