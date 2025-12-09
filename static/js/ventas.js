// 🟢 Leer productos desde el JSON embutido en el HTML
const productosDataElement = document.getElementById("productos-data");
const rawProductos = JSON.parse(productosDataElement.textContent);
const productos = rawProductos.map(p => p.fields);

// ✔ Referencias a elementos HTML
const productList = document.getElementById("product-list");
const search = document.getElementById("search");
const carritoBody = document.getElementById("carritoBody");

// ✔ Array donde se guarda el carrito
let carrito = [];


// 🟦 FUNCION PARA ACTUALIZAR FECHA Y HORA EN TIEMPO REAL
function updateDateTime(){
    const now = new Date();
    document.getElementById("fecha").textContent = now.toLocaleDateString();
    document.getElementById("hora").textContent = now.toLocaleTimeString();
}
setInterval(updateDateTime, 1000);
updateDateTime();


// 🟩 FUNCION QUE DIBUJA LOS PRODUCTOS EN PANTALLA
function renderProductos(filtro=""){
    productList.innerHTML = "";

    productos
        // ✔ Filtra por nombre si el usuario escribe en el buscador
        .filter(p => p.nombre.toLowerCase().includes(filtro.toLowerCase()))
        // ✔ Crea una tarjeta por cada producto
        .forEach(p => {
            const col = document.createElement("div");
            col.className = "col-6 col-md-4 col-xl-3";

            col.innerHTML = `
                <div class="card product-card p-2" data-codigo="${p.codigo}">
                    <h6>${p.nombre}</h6>
                    <p class="text-muted m-0">Código: ${p.codigo}</p>
                    <span class="fw-bold">$${p.precio.toLocaleString("es-CL")}</span>
                </div>
            `;

            // ✔ Agregar al carrito con click
            col.querySelector(".product-card").onclick = () => agregarCarrito(p.codigo);

            productList.appendChild(col);
        });
}
renderProductos();

// ✔ Buscador en tiempo real
search.oninput = () => renderProductos(search.value);


// 🟥 AGREGAR POR CÓDIGO
document.getElementById("btnBuscarCodigo").onclick = () => {
    const codigo = document.getElementById("codigoInput").value;
    agregarCarrito(codigo);
};


// 🟥 AÑADIR AL CARRITO
function agregarCarrito(codigo){
    const producto = productos.find(p=>p.codigo==codigo);

    // ✔ Si el producto no existe, avisa
    if(!producto){ alert("Código no encontrado"); return; }

    // ✔ Si ya existe en carrito → suma cantidad
    let item = carrito.find(i=>i.codigo==codigo);
    if(item){
        item.cantidad++;
    } else {
        carrito.push({...producto, cantidad:1});
    }

    renderCarrito();
}


// 🟥 DIBUJAR CARRITO
function renderCarrito(){
    carritoBody.innerHTML = "";

    carrito.forEach(item => {
        const fila = document.createElement("tr");

        fila.innerHTML = `
            <td>${item.codigo}</td>
            <td>${item.nombre}</td>
            <td>
                <input type="number" min="1" value="${item.cantidad}" class="form-control form-control-sm edit-qty">
            </td>
            <td>$${(item.precio * item.cantidad).toLocaleString("es-CL")}</td>
            <td>
                <button class="btn btn-sm btn-danger"><i class="bi bi-x"></i></button>
            </td>
        `;

        // ✔ Editar cantidad
        fila.querySelector("input").oninput = e => {
            item.cantidad = Number(e.target.value);
            renderCarrito();
        };

        // ✔ Eliminar producto del carrito
        fila.querySelector("button").onclick = () => {
            carrito = carrito.filter(x=>x.codigo != item.codigo);
            renderCarrito();
        };

        carritoBody.appendChild(fila);
    });

    calcularTotales();
}


// 🧮 CALCULA NETO, IVA Y TOTAL
function calcularTotales(){
    const neto = carrito.reduce((sum,i)=>sum+i.precio*i.cantidad,0);
    const iva = Math.round(neto * 0.19);
    const total = neto + iva;

    document.getElementById("neto").textContent = neto.toLocaleString("es-CL");
    document.getElementById("iva").textContent = iva.toLocaleString("es-CL");
    document.getElementById("total").textContent = total.toLocaleString("es-CL");
}


// 🟨 CAMPOS DE MÉTODO DE PAGO
document.getElementById("metodoPago").onchange = actualizarCamposPago;

function actualizarCamposPago(){
    const metodo = this.value;

    // ✔ Campos disponibles
    const campos = {
        efectivo: document.getElementById("montoEfectivo"),
        debito:   document.getElementById("montoDebito"),
        credito:  document.getElementById("montoCredito")
    };

    // ✔ Oculta todos
    Object.values(campos).forEach(c=>c.classList.add("d-none"));

    // ✔ Muestra según método
    if(metodo=="efectivo") campos.efectivo.classList.remove("d-none");
    if(metodo=="debito")   campos.debito.classList.remove("d-none");
    if(metodo=="credito")  campos.credito.classList.remove("d-none");
    if(metodo=="mixto")    Object.values(campos).forEach(c=>c.classList.remove("d-none"));
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
        alert("El carrito está vacío");
        return;
    }
    
    const data = {
        carrito: carrito,
        cliente_id: 1 // Cliente "Varios"
    };

    fetch(crearVentaUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success'){
            alert("Venta registrada con éxito!");
            window.location.href = listaVentasUrl;
        } else {
            alert("Error al registrar la venta: " + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Ocurrió un error inesperado.");
    });
};
