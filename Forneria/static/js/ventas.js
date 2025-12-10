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

const productos = JSON.parse(document.getElementById("productos-data").textContent);

// =========================
// Referencias HTML
// =========================
const productList = document.getElementById("product-list");
const search = document.getElementById("search");
const carritoBody = document.getElementById("carritoBody");

let carrito = []; // [{id, nombre, precio, cantidad, descuento_pct}]

// =========================
// Fecha y hora en tiempo real
// =========================
function updateDateTime() {
  const now = new Date();
  document.getElementById("fecha").textContent = now.toLocaleDateString('es-CL');
  document.getElementById("hora").textContent = now.toLocaleTimeString('es-CL');
}
setInterval(updateDateTime, 1000);
updateDateTime();

// =========================
// Render de productos
// =========================
function renderProductos(filtro = "") {
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
          <p class="text-muted m-0">Stock: ${p.stock_actual}</p>
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
// Agregar por ID manual
// =========================
document.getElementById("btnBuscarCodigo").onclick = () => {
  const idStr = document.getElementById("codigoInput").value.trim();
  const id = parseInt(idStr, 10);
  if (Number.isNaN(id)) { alert("ID inválido"); return; }
  agregarCarritoPorId(id);
};

// =========================
// Añadir al carrito con validación de stock
// =========================
function agregarCarritoPorId(id) {
  const producto = productos.find(p => p.id === id);
  if (!producto) { alert("Producto no encontrado"); return; }

  const item = carrito.find(i => i.id === id);
  if (item) {
    if (item.cantidad + 1 > producto.stock_actual) {
      alert(`No hay suficiente stock para ${producto.nombre}`);
      return;
    }
    item.cantidad = clamp(item.cantidad + 1, 1, producto.stock_actual);
  } else {
    if (producto.stock_actual <= 0) {
      alert(`Producto ${producto.nombre} sin stock disponible`);
      return;
    }
    carrito.push({ id: producto.id, nombre: producto.nombre, precio: producto.precio, cantidad: 1, descuento_pct: 0 });
  }

  renderCarrito();
}

// =========================
// Render del carrito
// =========================
function renderCarrito() {
  carritoBody.innerHTML = "";

  carrito.forEach(item => {
    const fila = document.createElement("tr");
    const subtotal = item.precio * item.cantidad * (1 - (item.descuento_pct || 0) / 100);

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

    const qtyInput = fila.querySelector(".edit-qty");
    qtyInput.oninput = e => {
      const val = parseInt(e.target.value, 10);
      const producto = productos.find(p => p.id === item.id);
      item.cantidad = clamp(Number.isNaN(val) ? 1 : val, 1, producto.stock_actual);
      renderCarrito();
    };

    fila.querySelector("button").onclick = () => {
      carrito = carrito.filter(x => x.id !== item.id);
      renderCarrito();
    };

    carritoBody.appendChild(fila);
  });

  calcularTotales();
}

// =========================
// Totales (UI)
function calcularTotales() {
  const neto = carrito.reduce((sum, i) => sum + i.precio * i.cantidad * (1 - (i.descuento_pct || 0) / 100), 0);
  const iva = Math.round(neto * 0.19);
  const total = neto + iva;

  document.getElementById("neto").textContent = numCL.format(neto);
  document.getElementById("iva").textContent = numCL.format(iva);
  document.getElementById("total").textContent = numCL.format(total);
}

// =========================
// Método de pago (UI)
document.getElementById("metodoPago").onchange = actualizarCamposPago;
function actualizarCamposPago() {
  const metodo = this.value;
  const campos = {
    efectivo: document.getElementById("montoEfectivo"),
    debito: document.getElementById("montoDebito"),
    credito: document.getElementById("montoCredito")
  };
  Object.values(campos).forEach(c => c.classList.add("d-none"));

  if (metodo === "efectivo") campos.efectivo.classList.remove("d-none");
  if (metodo === "debito") campos.debito.classList.remove("d-none");
  if (metodo === "credito") campos.credito.classList.remove("d-none");
  if (metodo === "mixto") Object.values(campos).forEach(c => c.classList.remove("d-none"));
}
actualizarCamposPago();

// =========================
// CSRF
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    document.cookie.split(';').forEach(cookie => {
      cookie = cookie.trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
      }
    });
  }
  return cookieValue;
}

// =========================
// Pagar
const crearVentaUrl = document.getElementById('ventas-js').getAttribute('data-url-crear-venta');
const listaVentasUrl = document.getElementById('ventas-js').getAttribute('data-url-lista-ventas');

document.getElementById("btnPagar").onclick = async () => {
  if (carrito.length === 0) { alert("El carrito está vacío"); return; }

  const btnPagar = document.getElementById("btnPagar");
  btnPagar.disabled = true;
  btnPagar.textContent = "Procesando...";

  const payload = {
    cliente_id: 1,
    canal_venta: 'TIENDA',
    carrito: carrito.map(i => ({ id: i.id, cantidad: i.cantidad, precio: i.precio, descuento_pct: i.descuento_pct })),
    pago_completo: true
  };

  try {
    const resp = await fetch(crearVentaUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
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
