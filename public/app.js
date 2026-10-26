// Brick Vault: interfaz que consume la API de FastAPI.
// Todo lo que se muestra viene de la base de datos por medio de fetch().

// ---------- Utilidades ----------
const $ = id => document.getElementById(id);

// Evita que un texto escrito por el usuario se interprete como HTML.
const esc = texto => String(texto ?? '').replace(/[&<>"']/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// Formas de mostrar un valor en la tabla según el tipo de columna.
const formatos = {
  texto: v => esc(v),
  num: v => esc(v),
  dinero: v => '₡' + Math.round(Number(v)).toLocaleString('es-CR'),
  fecha: v => esc(String(v).split('-').reverse().join('/')),
  pildora: v => `<span class="pildora" data-valor="${esc(v)}">${esc(v)}</span>`,
};

// Hace una petición a la API y devuelve el JSON. Si algo falla lanza un Error con un mensaje claro.
async function api(ruta, metodo = 'GET', cuerpo) {
  const opciones = { method: metodo };
  if (cuerpo) {
    opciones.headers = { 'Content-Type': 'application/json' };
    opciones.body = JSON.stringify(cuerpo);
  }
  let respuesta;
  try {
    respuesta = await fetch('/api/' + ruta, opciones);
  } catch {
    throw new Error('No hay conexión con el servidor. Revise que FastAPI esté en ejecución.');
  }
  if (respuesta.status === 204) return null;
  const datos = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    const detalle = datos && datos.detail;
    // FastAPI devuelve una lista cuando un dato no pasa la validación (error 422).
    if (Array.isArray(detalle)) {
      const campo = detalle[0].loc[detalle[0].loc.length - 1];
      throw new Error(`Revise el campo «${String(campo).replaceAll('_', ' ')}»: falta o no es válido.`);
    }
    throw new Error(detalle || 'El servidor no pudo completar la operación.');
  }
  return datos;
}

// ---------- Descripción de cada sección ----------
// columnas: qué se muestra en la tabla (t = título, c = campo, f = formato).
// campos: qué se pide en el formulario (n = nombre, e = etiqueta).
const secciones = {
  "sets": {
    "menu": "Sets",
    "titulo": "Sets de la colección",
    "nombre": "el set",
    "nuevo": "Registrar set",
    "ayuda": "Cada set se identifica con el número impreso en la caja.",
    "pk": "numero",
    "columnas": [
      {
        "t": "Número de set",
        "c": "numero",
        "f": "texto"
      },
      {
        "t": "Nombre",
        "c": "nombre",
        "f": "texto"
      },
      {
        "t": "Tema",
        "c": "tema_nombre",
        "f": "texto"
      },
      {
        "t": "Estado",
        "c": "estado",
        "f": "pildora"
      },
      {
        "t": "Piezas",
        "c": "piezas",
        "f": "num"
      },
      {
        "t": "Año",
        "c": "anno",
        "f": "num"
      },
      {
        "t": "Precio pagado",
        "c": "precio",
        "f": "dinero"
      },
      {
        "t": "Faltan",
        "c": "piezas_faltantes",
        "f": "num"
      }
    ],
    "campos": [
      {
        "n": "numero",
        "e": "Número de set",
        "tipo": "text",
        "clave": true
      },
      {
        "n": "nombre",
        "e": "Nombre",
        "ancho": true,
        "tipo": "text"
      },
      {
        "n": "tema",
        "e": "Tema",
        "fuente": {
          "ruta": "temas",
          "valor": "id",
          "texto": "nombre",
          "conClave": false,
          "falta": "Primero registre tema en «Temas»."
        }
      },
      {
        "n": "estado",
        "e": "Estado",
        "op": [
          "En caja",
          "Armado",
          "En exhibición",
          "Desarmado"
        ]
      },
      {
        "n": "piezas",
        "e": "Piezas",
        "tipo": "number",
        "paso": 1,
        "min": 1
      },
      {
        "n": "anno",
        "e": "Año",
        "tipo": "number",
        "paso": 1,
        "min": 1
      },
      {
        "n": "precio",
        "e": "Precio pagado (₡)",
        "tipo": "number",
        "paso": 0.01,
        "min": 0
      }
    ]
  },
  "faltantes": {
    "menu": "Piezas faltantes",
    "titulo": "Piezas faltantes",
    "nombre": "la pieza",
    "nuevo": "Registrar pieza",
    "ayuda": "Piezas perdidas que hay que reponer. Al registrarlas, el set queda marcado como incompleto.",
    "pk": "id",
    "columnas": [
      {
        "t": "Set",
        "c": "set_lego_nombre",
        "f": "texto"
      },
      {
        "t": "Pieza",
        "c": "descripcion",
        "f": "texto"
      },
      {
        "t": "Color",
        "c": "color",
        "f": "texto"
      },
      {
        "t": "Cantidad",
        "c": "cantidad",
        "f": "num"
      }
    ],
    "campos": [
      {
        "n": "set_lego",
        "e": "Set",
        "ancho": true,
        "fuente": {
          "ruta": "sets",
          "valor": "numero",
          "texto": "nombre",
          "conClave": true,
          "falta": "Primero registre set en «Sets»."
        }
      },
      {
        "n": "descripcion",
        "e": "Pieza",
        "tipo": "text"
      },
      {
        "n": "color",
        "e": "Color",
        "tipo": "text"
      },
      {
        "n": "cantidad",
        "e": "Cantidad",
        "tipo": "number",
        "paso": 1,
        "min": 1
      }
    ]
  },
  "minifiguras": {
    "menu": "Minifiguras",
    "titulo": "Minifiguras",
    "nombre": "la minifigura",
    "nuevo": "Registrar minifigura",
    "ayuda": "Personajes que vienen en cada set.",
    "pk": "id",
    "columnas": [
      {
        "t": "Nombre",
        "c": "nombre",
        "f": "texto"
      },
      {
        "t": "Set",
        "c": "set_lego_nombre",
        "f": "texto"
      },
      {
        "t": "Cantidad",
        "c": "cantidad",
        "f": "num"
      }
    ],
    "campos": [
      {
        "n": "nombre",
        "e": "Nombre",
        "ancho": true,
        "tipo": "text"
      },
      {
        "n": "set_lego",
        "e": "Set",
        "fuente": {
          "ruta": "sets",
          "valor": "numero",
          "texto": "nombre",
          "conClave": true,
          "falta": "Primero registre set en «Sets»."
        }
      },
      {
        "n": "cantidad",
        "e": "Cantidad",
        "tipo": "number",
        "paso": 1,
        "min": 1
      }
    ]
  },
  "temas": {
    "menu": "Temas",
    "titulo": "Temas",
    "nombre": "el tema",
    "nuevo": "Registrar tema",
    "ayuda": "Líneas de LEGO a las que pertenecen los sets.",
    "pk": "id",
    "columnas": [
      {
        "t": "Nombre",
        "c": "nombre",
        "f": "texto"
      },
      {
        "t": "Descripción",
        "c": "descripcion",
        "f": "texto"
      }
    ],
    "campos": [
      {
        "n": "nombre",
        "e": "Nombre",
        "tipo": "text"
      },
      {
        "n": "descripcion",
        "e": "Descripción",
        "ancho": true,
        "tipo": "textarea"
      }
    ]
  }
};

// ---------- Estado de la pantalla ----------
let actual = 'sets';   // sección que se está viendo
let filas = [];              // registros recibidos de la API
let editando = null;         // llave del registro en edición (null si se está creando)

// ---------- Menú y tabla ----------
function pintarMenu() {
  const botones = Object.entries(secciones).map(([clave, s]) => [clave, s.menu]);
  botones.push(['resumen', 'Resumen']);
  $('menu').innerHTML = botones.map(([clave, texto]) =>
    `<button type="button" data-seccion="${clave}" ${clave === actual ? 'aria-current="page"' : ''}>${texto}</button>`
  ).join('');
}

function elegir(seccion) {
  actual = seccion;
  const s = secciones[actual];
  $('titulo').textContent = s ? s.titulo : 'Resumen';
  $('ayuda').textContent = s ? s.ayuda : 'Datos calculados por el backend con consultas a la base de datos.';
  $('btn-nuevo').hidden = !s;
  if (s) $('btn-nuevo').textContent = s.nuevo;
  pintarMenu();
  cargar();
}

// Pide los registros de la sección actual (GET) y vuelve a dibujar la tabla.
async function cargar() {
  try {
    filas = await api(actual);
  } catch (error) {
    filas = [];
    avisar(error.message, true);
  }
  if (actual === 'resumen') pintarResumen(); else pintarTabla();
}

function pintarTabla() {
  const s = secciones[actual];
  $('cabeza').innerHTML = '<tr>' +
    s.columnas.map(c => `<th${c.f === 'num' || c.f === 'dinero' ? ' class="num"' : ''}>${c.t}</th>`).join('') +
    '<th><span hidden>Acciones</span></th></tr>';
  $('cuerpo').innerHTML = filas.map(fila => {
    const pk = esc(fila[s.pk]);
    return '<tr>' +
      s.columnas.map(c => `<td${c.f === 'num' || c.f === 'dinero' ? ' class="num"' : ''}>${formatos[c.f](fila[c.c])}</td>`).join('') +
      `<td class="botones">
         <button class="btn chico" data-accion="editar" data-pk="${pk}">Editar</button>
         <button class="btn chico peligro" data-accion="eliminar" data-pk="${pk}">Eliminar</button>
       </td></tr>`;
  }).join('');
  $('vacio').hidden = filas.length > 0;
  $('vacio').textContent = `Todavía no hay registros. Use «${s.nuevo}» para agregar el primero.`;
}

// El resumen llega como una lista de { dato, valor } ya calculada por FastAPI.
function pintarResumen() {
  $('cabeza').innerHTML = '';
  $('cuerpo').innerHTML = filas.map(f => `<tr><td class="dato">${esc(f.dato)}</td><td>${esc(f.valor)}</td></tr>`).join('');
  $('vacio').hidden = filas.length > 0;
  $('vacio').textContent = 'No se pudo cargar el resumen.';
}

// ---------- Formulario ----------
// Dibuja un campo: lista desplegable, área de texto o entrada normal.
function htmlCampo(campo, valor = '') {
  let control;
  if (campo.opciones) {
    control = `<select name="${campo.n}" required>` + campo.opciones.map(([v, t]) =>
      `<option value="${esc(v)}" ${String(v) === String(valor) ? 'selected' : ''}>${esc(t)}</option>`).join('') + '</select>';
  } else if (campo.tipo === 'textarea') {
    control = `<textarea name="${campo.n}" ${campo.opcional ? '' : 'required'}>${esc(valor)}</textarea>`;
  } else {
    const bloqueado = campo.clave && editando !== null ? 'readonly' : '';
    const numero = campo.tipo === 'number' ? `min="${campo.min}" step="${campo.paso}"` : '';
    control = `<input name="${campo.n}" type="${campo.tipo}" value="${esc(valor)}" ${numero} ${bloqueado} required>`;
  }
  return `<label class="campo${campo.ancho ? ' ancho' : ''}">${campo.e}${control}</label>`;
}

async function abrirFormulario(pk = null) {
  const s = secciones[actual];
  const palabra = s.nombre.split(' ').slice(1).join(' ');
  editando = pk;
  const fila = pk === null ? {} : filas.find(f => String(f[s.pk]) === String(pk));
  const hoy = new Date().toLocaleDateString('en-CA');   // formato AAAA-MM-DD
  try {
    const partes = [];
    for (const campo of s.campos) {
      // Si el campo depende de otra tabla (llave foránea), las opciones se piden a la API.
      if (campo.fuente) {
        const lista = await api(campo.fuente.ruta);
        if (!lista.length) throw new Error(campo.fuente.falta);
        campo.opciones = lista.map(x => [x[campo.fuente.valor],
          campo.fuente.conClave ? `${x[campo.fuente.valor]} ${x[campo.fuente.texto]}` : x[campo.fuente.texto]]);
      } else if (campo.op) {
        campo.opciones = campo.op.map(o => [o, o]);
      }
      partes.push(htmlCampo(campo, fila[campo.n] ?? (campo.tipo === 'date' ? hoy : '')));
    }
    $('form-campos').innerHTML = partes.join('');
  } catch (error) {
    return avisar(error.message, true);
  }
  $('form-error').hidden = true;
  $('form-titulo').textContent = pk === null ? s.nuevo : 'Editar ' + palabra;
  $('form-guardar').textContent = 'Guardar ' + palabra;
  $('dlg-form').showModal();
}

// Lee el formulario y arma el objeto que se enviará como JSON.
function leerFormulario() {
  const datos = Object.fromEntries(new FormData($('form')));
  for (const campo of secciones[actual].campos) {
    // Los números y las llaves foráneas numéricas viajan como número, no como texto.
    const esNumero = campo.tipo === 'number' || (campo.fuente && !campo.fuente.conClave);
    if (esNumero) datos[campo.n] = Number(datos[campo.n]);
  }
  return datos;
}

// Envía el formulario: POST si es un registro nuevo, PUT si se está editando.
async function guardar(evento) {
  evento.preventDefault();
  if (!$('form').reportValidity()) return;
  const s = secciones[actual];
  const ruta = editando === null ? actual : `${actual}/${encodeURIComponent(editando)}`;
  try {
    await api(ruta, editando === null ? 'POST' : 'PUT', leerFormulario());
    $('dlg-form').close();
    avisar(`Se guardó ${s.nombre}.`);
    cargar();
  } catch (error) {
    $('form-error').textContent = error.message;
    $('form-error').hidden = false;
  }
}

async function eliminar(pk) {
  const s = secciones[actual];
  if (!confirm(`¿Eliminar ${s.nombre}? No se puede deshacer.`)) return;
  try {
    await api(`${actual}/${encodeURIComponent(pk)}`, 'DELETE');
    avisar(`Se eliminó ${s.nombre}.`);
    cargar();
  } catch (error) {
    avisar(error.message, true);
  }
}

// ---------- Avisos ----------
let reloj;
function avisar(texto, malo = false) {
  const aviso = $('aviso');
  aviso.textContent = texto;
  aviso.classList.toggle('malo', malo);
  aviso.hidden = false;
  clearTimeout(reloj);
  reloj = setTimeout(() => { aviso.hidden = true; }, 4500);
}

// ---------- Eventos ----------
// Un solo "escucha" para todos los botones: se revisa qué botón recibió el clic.
document.addEventListener('click', evento => {
  const boton = evento.target.closest('button');
  if (!boton) return;
  const { seccion, accion, pk } = boton.dataset;
  if (seccion) elegir(seccion);
  else if (accion === 'editar') abrirFormulario(pk);
  else if (accion === 'eliminar') eliminar(pk);
});
$('btn-nuevo').addEventListener('click', () => abrirFormulario());
$('form-cancelar').addEventListener('click', () => $('dlg-form').close());
$('form').addEventListener('submit', guardar);

elegir(actual);
