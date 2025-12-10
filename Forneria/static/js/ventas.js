
// =========================
// Utilidades
// =========================
const CLP = new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 });
const numCL = new Intl.NumberFormat('es-CL');

function clamp(n, min, max) {
  return Math.max(min, Math.min(max, n));
}

// =========================
// Datos embebidos
// =========================
const productosDataElement = document.getElementById("productos-data");
const rawProductos = JSON.parse(productosDataElement.textContent);

// rawProductos viene del serializer de Django: [{model:..., pk:..., fields:{nombre, precio}}...]
const productos = rawProductos.map(p => ({
  id: p.pk,                    // ⚠️ usamos id (no codigo)
  nombre: p.fields.nombre,
  precio: Number(p.fields.precio), // viene como string, lo convertimos para UI
  // opcional: incluir stock_actual si lo serializas desde Django
  // stock_actual: p.fields.stock_actual
}));

// =========================
// Referencias HTML
// =========================
const productList = document.getElementById("product-list");
const search = document.getElementById("search");
const carritoBody = document.getElementById("carritoBody");

// Estado
let carrito = []; // [{id, nombre, precio, cantidad}]

// =========================
// Fecha y hora en tiempo real
// =========================
function updateDateTime(){
  const now = new Date();
  document.getElementById("fecha").textContent = now.toLocaleDateString('es-CL');
  document.getElementById("hora").textContent = now.toLocaleTimeString('es-CL');
}
setInterval(updateDateTime, 1000);
updateDateTime();

// =========================
/** Render de productos */
// =========================
function renderProductos(filtro = ""){
  productList.innerHTML = "";

  productos
    .filter(p => p.nombre.toLowerCase().includes(filtro.toLowerCase()))
    .forEach(p => {
      const col = document.createElement("div");
      col.className = "col-6 col-md-4 col-xl-3";

      col.innerHTML = `
        <div class="card product-card p-2" data-id="${p.id}">
          <h6>${p.nombre}</h6>
          <p class="text-muted m-0">ID: ${p.id}</p>
          <span class="fw-bold">${CLP.format(p.precio)}</span>
        </div>
      `;

      col.querySelector(".product-card").onclick = () => agregarCarritoPorId(p.id);
      productList.appendChild(col);
    });
}
renderProductos();

// Debounce del buscador
let searchTimer = null;
search.oninput = () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => renderProductos(search.value), 200);
};

// =========================
/** Agregar por ID manual */
// =========================
document.getElementById("btnBuscarCodigo").onclick = () => {
  // ahora tomamos ID en vez de "codigo"
  const idStr = document.getElementById("codigoInput").value.trim();
  const id = parseInt(idStr, 10);
  if (Number.isNaN(id)) {
    alert("ID inválido");
    return;
  }
  agregarCarritoPorId(id);
};

// =========================
/** Añadir al carrito */
// =========================
function agregarCarritoPorId(id){
  const producto = productos.find(p => p.id === id);

  if (!producto) { alert("Producto no encontrado"); return; }

  // Si ya existe en carrito, suma cantidad; si no, agrega
  const item = carrito.find(i => i.id === id);
  if (item) {
    item.cantidad = clamp(item.cantidad + 1, 1, 9999);
  } else {
    carrito.push({ id: producto.id, nombre: producto.nombre, precio: producto.precio, cantidad: 1 });
  }

  renderCarrito();
}

// =========================
/** Render del carrito */
// =========================
function renderCarrito(){
  carritoBody.innerHTML = "";

  carrito.forEach(item => {
    const fila = document.createElement("tr");
    const subtotal = item.precio * item.cantidad;

    fila.innerHTML = `
      <td>${item.id}</td>
      <td>${item.nombre}</td>
      <td>
        <input type="number" min="1" value="${item.cantidad}" class="form-control form-control-sm edit-qty">
      </td>
      <td>${CLP.format(subtotal)}</td>
      <td>
        <button class="btn btn-sm btn-danger"><i class="bi bi-x"></i></button>
      </td>
    `;

    // editar cantidad
    const qtyInput = fila.querySelector(".edit-qty");
    qtyInput.oninput = e => {
      const val = parseInt(e.target.value, 10);
      item.cantidad = clamp(Number.isNaN(val) ? 1 : val, 1, 9999);
      renderCarrito();
    };

    // eliminar producto
    fila.querySelector("button").onclick = () => {
      carrito = carrito.filter(x => x.id !== item.id);
      renderCarrito();
    };

    carritoBody.appendChild(fila);
  });

  calcularTotales();
}

// =========================
/** Totales (UI) */
// =========================
function calcularTotales(){
  const neto = carrito.reduce((sum, i) => sum + i.precio * i.cantidad, 0);
  const iva = Math.round(neto * 0.19); // UI: CLP entero; backend calcula con Decimal
  const total = neto + iva;

  document.getElementById("neto").textContent = numCL.format(neto);
  document.getElementById("iva").textContent = numCL.format(iva);
  document.getElementById("total").textContent = numCL.format(total);
}

// =========================
/** Método de pago (UI) */
// =========================
document.getElementById("metodoPago").onchange = actualizarCamposPago;

function actualizarCamposPago(){
  const metodo = this.value;
  const campos = {
    efectivo: document.getElementById("montoEfectivo"),
    debito:   document.getElementById("montoDebito"),
    credito:  document.getElementById("montoCredito")
  };
  Object.values(campos).forEach(c => c.classList.add("d-none"));

  if (metodo === "efectivo") campos.efectivo.classList.remove("d-none");
  if (metodo === "debito")   campos.debito.classList.remove("d-none");
  if (metodo === "credito")  campos.credito.classList.remove("d-none");
  if (metodo === "mixto")    Object.values(campos).forEach(c => c.classList.remove("d-none"));
}
actualizarCamposPago();

// =========================
/** CSRF */
// =========================
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// =========================
/** Pagar */
// =========================
const crearVentaUrl = document.getElementById('ventas-js').getAttribute('data-url-crear-venta');
const listaVentasUrl = document.getElementById('ventas-js').getAttribute('data-url-lista-ventas');

const btnPagar = document.getElementById("btnPagar");
btnPagar.onclick = async () => {
  if (carrito.length === 0) {
    alert("El carrito está vacío");
    return;
  }

  // Deshabilita para evitar doble click
  btnPagar.disabled = true;
  btnPagar.textContent = "Procesando...";

  // Payload mínimo requerido por el backend
  const payload = {
    cliente_id: 1, // Cliente genérico "Varios"
    canal_venta: 'TIENDA',
    carrito: carrito.map(i => ({
      id: i.id,
      cantidad: i.cantidad,
      precio: i.precio,           // si confías en el precio del servidor, podrías omitir y tomarlo desde BD
      // descuento_pct: 0
    })),
    pago_completo: true
  };

  try {
    const resp = await fetch(crearVentaUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify(payload)
    });

    const data = await resp.json();
    if (data.status === 'success') {
      alert("Venta registrada con éxito!");
      window.location.href = listaVentasUrl;
    } else {
      alert("Error al registrar la venta: " + (data.message || 'Error desconocido'));
    }
  } catch (err) {
    console.error('Error:', err);
    alert("Ocurrió un error inesperado.");
  } finally {
    btnPagar.disabled = false;
    btnPagar.textContent = "Pagar";
  }
};
