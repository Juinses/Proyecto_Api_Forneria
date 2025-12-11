# 🎨 Guía para Frontend / Diseño

## 📂 Ubicaciones clave en el proyecto:

- **Plantilla POS principal**: `templates/ventas/form.html`
- **Script del carrito**: `static/js/ventas.js` (Línea ~15-20: función `mostrarNotificacion`)
- **Plantilla base**: `templates/base.html` (Línea ~17: carga SweetAlert2)
- **Manejo de confirmaciones**: `templates/base.html` línea ~ (script para `.btn-eliminar`)

---

## ⚠️ IMPORTANTE: No rompas esto

Estos elementos HTML son críticos y **NO deben ser renombrados o movidos** sin coordinar con backend:

### IDs de elementos que JavaScript usa (en `templates/ventas/form.html`):
```html
<!-- Buscador (línea ~) -->
<input id="search" .../>                   <!-- Buscar producto por nombre -->
<input id="codigoInput" .../>              <!-- Input para agregar por código -->
<button id="btnBuscarCodigo">...</button>  <!-- Botón agregar por ID -->

<!-- Productos y carrito (línea ~) -->
<div id="product-list"></div>              <!-- Donde se pintan las tarjetas de productos -->
<tbody id="carritoBody"></tbody>           <!-- Tabla con items del carrito -->

<!-- Totales (línea ~) -->
<strong id="neto">0</strong>               <!-- Total sin IVA -->
<strong id="iva">0</strong>                <!-- Total IVA (19%) -->
<strong id="total">0</strong>              <!-- Total con IVA -->

<!-- Pago (línea ~) -->
<select id="metodoPago">...</select>       <!-- Selector de método de pago -->
<div id="montoEfectivo">...</div>          <!-- Campo para monto efectivo -->
<div id="montoDebito">...</div>            <!-- Campo para monto débito -->
<div id="montoCredito">...</div>           <!-- Campo para monto crédito -->
<button id="btnPagar">...</button>         <!-- Botón para pagar -->

<!-- Scripts que proporcionan datos (línea ~) -->
<script id="productos-data">
  <!-- JSON de productos del servidor (procesado en static/js/ventas.js línea 16-21) -->
</script>
<script id="ventas-js" 
  data-url-crear-venta="URL" 
  data-url-lista-ventas="URL">
</script>
```

### Clases CSS requeridas:
```html
<!-- En templates/inventario/lista.html línea ~ y templates/ventas/lista_ventas.html -->
<!-- Botones de eliminar (convertidos a SweetAlert2 automáticamente) -->
<a class="btn-eliminar" data-mensaje="¿Eliminar?">
  <i class="bi bi-trash"></i>
</a>
<!-- Manejado por: templates/base.html línea ~ (detector de clicks en .btn-eliminar) -->
```

## 📝 Flujo de datos - Diagrama simple

```
1. Usuario abre /ventas/nuevo/ (apps/ventas/views.py línea ~)
   ↓
2. Servidor envía HTML + datos:
   - Plantilla: templates/ventas/form.html
   - JSON en <script id="productos-data">
   - URLs en <script id="ventas-js">
   ↓
3. JavaScript (static/js/ventas.js) carga:
   - Lee productos del JSON (línea 16-21)
   - Dibuja tarjetas en #product-list (función renderProductos, línea ~)
   ↓
4. Usuario selecciona productos:
   - Click en producto → agregarCarritoPorId() (línea ~)
   - Se agrega a array "carrito" en memoria
   - Renderiza tabla en #carritoBody (función renderCarrito, línea ~)
   ↓
5. Usuario hace click en "Pagar":
   - Valida carrito no esté vacío (muestra SweetAlert, línea ~)
   - Obtiene token CSRF (función getCookie, línea ~)
   - Envía POST /ventas/nuevo/ con JSON (línea ~)
   ↓
6. Backend procesa (apps/ventas/views.py línea 40):
   - Crea Venta y DetalleVenta
   - Calcula totales
   - Retorna {status: 'success', venta_id: X}
   ↓
7. JavaScript redirige a /ventas/listado/ con notificación
```

## 🔍 Qué necesitas saber:

### Backend maneja:
✅ Guardar datos en BD
✅ Validar datos
✅ Calcular totales (recalcular_totales)
✅ Crear cliente si no existe
✅ Autenticación y permisos
✅ Error CSRF

### Frontend maneja:
✅ Mostrar productos bonitos
✅ Agregar/quitar del carrito (sin servidor)
✅ Calcular totales (neto, IVA, total)
✅ Seleccionar método de pago
✅ Enviar al servidor cuando hace click "Pagar"
✅ Mostrar errores amigables

---

## 🎯 Qué puedes cambiar sin romper nada:

### ✅ SÍ puedes cambiar:
- Estilos CSS (colores, tamaños, fonts)
- HTML estructura visual (clases, divs adicionales)
- Textos en las páginas
- Imágenes
- Diseño del layout
- Animaciones CSS
- Bootstrap clases

### ❌ NO puedes cambiar:
- IDs de elementos (product-list, btnPagar, etc.)
- Clases requeridas: `btn-eliminar` (botones de confirmar eliminación)
- Atributos data-* de scripts
- Estructura del carrito en la tabla
- Nombres de inputs en formularios
- Orden de inputs en formularios
- Endpoints URLs

---

## 📱 Ejemplo: Cambiar diseño de tarjeta de producto

**Dónde editar**: `/static/js/ventas.js` (función `renderProductos`)

```javascript
// ACTUAL:
col.innerHTML = `
    <div class="card product-card p-2" data-id="${p.id}">
        <h6>${p.nombre}</h6>
        <p class="text-muted m-0">ID: ${p.id}</p>
        <span class="fw-bold">${CLP.format(p.precio)}</span>
        <p class="text-muted m-0">Stock: ${p.stock_actual}</p>
    </div>
`;

// PUEDES CAMBIAR A:
col.innerHTML = `
    <div class="card product-card p-2 shadow" data-id="${p.id}">
        <h5 class="text-primary">${p.nombre}</h5>
        <p class="text-muted small">Código: ${p.id}</p>
        <h4 class="text-success">${CLP.format(p.precio)}</h4>
        <small class="badge bg-warning">Disponible</small>
    </div>
`;

// ✅ Cambias clases y textos
// ❌ Pero NO cambias: data-id, ${p.id}, ${p.nombre}, etc.
```

---

## � Notificaciones (SweetAlert2)

El sistema ahora usa **SweetAlert2** en lugar de `alert()` y `confirm()` del navegador:

### Automáticas:
- ✅ **Errores al agregar productos** → Notificación roja
- ✅ **Carrito vacío al pagar** → Notificación amarilla  
- ✅ **Venta registrada** → Notificación verde
- ✅ **Confirmar eliminación** → Notificación de confirmación

### No necesitas hacer nada, funcionan automáticamente en:
- `/ventas/nuevo/` → Todas las operaciones
- `/inventario/lista/` → Botones de eliminar
- `/ventas/listado/` → Botones de eliminar

---

## �🔗 Endpoints que el Frontend usa

### GET (cargar páginas):
```
GET /                        → Inicio
GET /login/                  → Login
GET /ventas/                 → Home ventas
GET /ventas/nuevo/           → POS (carrito)
  - Response: HTML + JSON en <script id="productos-data">
GET /ventas/listado/         → Historial
GET /inventario/             → Inventario (solo admin)
```

### POST (JSON desde JavaScript):
```
POST /ventas/nuevo/
Headers: 
  - Content-Type: application/json
  - X-CSRFToken: [se obtiene automáticamente de cookies]
Body:
{
  "cliente_id": 1,
  "carrito": [{id, nombre, precio, cantidad, descuento_pct}, ...],
  "canal_venta": "TIENDA",
  "folio": "V-001"
}
Response:
  {status: "success", venta_id: 42}
  o
  {status: "error", message: "..."}
```

---

## 🎨 Paleta sugerida de cambios

### Cambiar colores del botón "Pagar":
```html
<!-- Original: -->
<button id="btnPagar" class="btn btn-success btn-lg">

<!-- Cambiar a (por ejemplo, azul): -->
<button id="btnPagar" class="btn btn-primary btn-lg">
```

### Cambiar estilo de la tabla del carrito:
```html
<!-- Original: -->
<table class="table table-sm table-striped align-middle">

<!-- Cambiar a (por ejemplo, bordes): -->
<table class="table table-sm table-bordered align-middle">
```

### Agregar icono a producto (sin romper):
```html
<!-- Original: -->
<span class="fw-bold">${CLP.format(p.precio)}</span>

<!-- Cambiar a: -->
<span class="fw-bold">💵 ${CLP.format(p.precio)}</span>
```

---

## 📋 Checklist antes de subir cambios

- [ ] Los IDs siguen siendo los mismos
- [ ] El JSON de productos sigue en `<script id="productos-data">`
- [ ] Las URLs en `<script id="ventas-js">` siguen presentes
- [ ] El input de búsqueda sigue siendo `id="search"`
- [ ] La tabla del carrito sigue siendo `id="carritoBody"`
- [ ] El botón pagar sigue siendo `id="btnPagar"`
- [ ] Sin errores de consola (F12 → Console)
- [ ] Las ventas se siguen guardando correctamente

---

## 🚨 Si algo se rompe:

### Paso 1: Abre la consola (F12)
Mira si hay errores en rojo.

### Paso 2: Revisa qué cambiaste
¿Renombraste un ID? ¿Moviste un elemento?

### Paso 3: Compara con DOCUMENTACION_API.md
Verifica que no hayas tocado elementos críticos.

### Paso 4: Avisa al backend
Describe exactamente qué cambiaste.

---

## 💡 Tips útiles

### Para probar cambios:
```bash
# Terminal en carpeta del proyecto
python manage.py runserver

# Abre en navegador
http://localhost:8000/ventas/nuevo/
```

### Para ver el JSON de productos:
```javascript
// Abre consola (F12) y escribe:
console.log(productos);
// Verás el array de productos
```

### Para ver el carrito actual:
```javascript
// Abre consola (F12) y escribe:
console.log(carrito);
// Verás lo que hay en el carrito
```

---

**Preguntas frecuentes:**

**P: ¿Puedo cambiar el orden de los campos?**
R: Sí, en templates (HTML). No en los modelos Django.

**P: ¿Puedo agregar más campos al formulario?**
R: Sí, pero coordina con backend para que los procese.

**P: ¿Cómo cambio los textos?**
R: Directo en los templates HTML o en `ventas.js`.

**P: ¿Qué pasa si rompo algo?**
R: Git permite deshacer cambios. `git restore <archivo>`

---

**¡Listo! Ahora puedes diseñar sin miedo de romper el backend. 🎨**
