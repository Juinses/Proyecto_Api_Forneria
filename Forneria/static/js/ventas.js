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

// Normalizamos para usar SIEMPRE id / nombre / precio / stock_actual
const productos = rawProductos.map(p => ({
    id: p.pk,
    nombre: p.fields.nombre,
    precio: Number(p.fields.precio),
    stock_actual: p.fields.stock_actual || 0
}));

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
    const fechaEl = document.getElementById("fecha");
    const horaEl = document.getElementById("hora");
    
    if (fechaEl && horaEl) {
        const now = new Date();
        fechaEl.textContent = now.toLocaleDateString('es-CL');
        horaEl.textContent = now.toLocaleTimeString('es-CL');
    }
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

// Debounce buscador
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
    if (Number.isNaN(id)) { 
        mostrarNotificacion("Error", "ID inválido. Ingresa un número válido.", "error");
        return; 
    }
    agregarCarritoPorId(id);
};

// =========================
// Añadir al carrito con validación de stock
// =========================
function agregarCarritoPorId(id) {
    const producto = productos.find(p => p.id === id);
    if (!producto) { 
        mostrarNotificacion("Error", "Producto no encontrado en el sistema.", "error");
        return; 
    }

    const item = carrito.find(i => i.id === id);

    if (item) {
        item.cantidad = item.cantidad + 1;
    } else {
        carrito.push({ 
            id: producto.id,
            nombre: producto.nombre,
            precio: producto.precio,
            cantidad: 1,
            descuento_pct: 0
        });
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
            item.cantidad = Number.isNaN(val) || val < 1 ? 1 : val;
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
// =========================
function calcularTotales() {
    const neto = carrito.reduce((sum, i) =>
        sum + i.precio * i.cantidad * (1 - (i.descuento_pct || 0) / 100), 0
    );

    const iva = Math.round(neto * 0.19);
    const total = neto + iva;

    document.getElementById("neto").textContent = numCL.format(neto);
    document.getElementById("iva").textContent = numCL.format(iva);
    document.getElementById("total").textContent = numCL.format(total);
}

// =========================
// Método de pago (UI)
// =========================
document.getElementById("metodoPago").onchange = actualizarCamposPago;
function actualizarCamposPago() {
    const metodo = this.value;

    // ✔ Campos disponibles
    const campos = {
        efectivo: document.getElementById("montoEfectivo"),
        debito: document.getElementById("montoDebito"),
        credito: document.getElementById("montoCredito")
    };

    // ✔ Oculta todos
    Object.values(campos).forEach(c => c.classList.add("d-none"));

    // ✔ Muestra según método
    if (metodo === "efectivo") campos.efectivo.classList.remove("d-none");
    if (metodo === "debito") campos.debito.classList.remove("d-none");
    if (metodo === "credito") campos.credito.classList.remove("d-none");
    if (metodo === "mixto") Object.values(campos).forEach(c => c.classList.remove("d-none"));
}
actualizarCamposPago();

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

// 🟢 BOTÓN PAGAR
const crearVentaUrl = document.getElementById('ventas-js').getAttribute('data-url-crear-venta');

const listaVentasUrl = document.getElementById('ventas-js').getAttribute('data-url-lista-ventas');

document.getElementById("btnPagar").onclick = () => {
    if(carrito.length === 0){
        mostrarNotificacion("Carrito Vacío", "Agrega productos al carrito antes de pagar.", "warning");
        return;
    }

    // Obtener cliente seleccionado
    const clienteSelect = document.getElementById("cliente");
    const clienteId = clienteSelect.value;
    if (!clienteId) {
        mostrarNotificacion("Error", "Debes seleccionar un cliente antes de pagar.", "error");
        return;
    }

    const data = {
        carrito: carrito,
        cliente_id: clienteId,
        pago_completo: true, // si quieres asumir pago completo
        folio: "F001" // o tu lógica para generar folio dinámico
    };

    fetch(crearVentaUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        const contentType = response.headers.get('content-type') || '';
        if (!response.ok) {
            if (contentType.includes('application/json')) {
                return response.json().then(err => { throw new Error(err.message || 'Error desconocido'); });
            } else {
                return response.text().then(txt => { throw new Error('Respuesta inesperada del servidor'); });
            }
        }
        return response.json();
    })
    .then(data => {
        if(data.status === 'success'){
            mostrarNotificacion("Éxito", "Venta registrada correctamente. Redirigiendo...", "success");
            setTimeout(() => {
                window.location.href = listaVentasUrl;
            }, 1500);
        } else {
            mostrarNotificacion("Error", "Error al registrar la venta: " + (data.message || 'Error desconocido'), "error");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarNotificacion("Error de Conexión", "Ocurrió un error: " + error.message, "error");
    });
};


