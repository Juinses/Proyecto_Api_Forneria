# 📚 Documentación del API - Fornería

## 🎯 Resumen General

Este es un sistema de gestión de ventas e inventario para una panadería. El proyecto está dividido en:
- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript (Bootstrap + SweetAlert2)

---

## 🏗️ Estructura del Proyecto

```
Forneria/
├── Forneria/                 # Configuración principal
│   ├── settings.py          # Configuración de Django
│   ├── urls.py              # Rutas principales
│   ├── views.py             # Vista de error CSRF
│   └── wsgi.py / asgi.py
├── apps/
│   ├── inventario/          # Gestión de productos
│   │   ├── models.py        # Modelos: Productos, Categorías, Nutricional
│   │   ├── views.py         # Vistas CRUD de inventario
│   │   ├── urls.py          # Rutas de inventario
│   │   └── forms.py         # Formularios
│   └── ventas/              # Gestión de ventas
│       ├── models.py        # Modelos: Ventas, Clientes, DetalleVenta
│       ├── views.py         # Vistas de ventas (API JSON + HTML)
│       ├── urls.py          # Rutas de ventas
│       └── forms.py         # Formularios
├── templates/               # Plantillas HTML
│   ├── base.html           # Plantilla base
│   ├── login.html          # Login
│   ├── csrf_failure.html   # Error CSRF
│   ├── inventario/         # Plantillas de inventario
│   └── ventas/             # Plantillas de ventas
├── static/
│   ├── css/                # Estilos CSS
│   └── js/                 # JavaScript
│       └── ventas.js       # Lógica del carrito de ventas
└── manage.py
```

---

## 🔐 Roles y Permisos

### Roles disponibles:
1. **Superuser (Admin)**: Acceso total al inventario y ventas
2. **Vendedor**: Solo puede hacer ventas, **NO** puede acceder a inventario
3. **Sin autenticación**: Redirigido al login

### Restricciones por rol:

| Ruta | Admin | Vendedor |
|------|-------|----------|
| `/admin/` | ✅ | ❌ |
| `/inventario/` | ✅ | ❌ Redirige a `/` |
| `/ventas/` | ✅ | ✅ |
| `/login/` | ✅ | ✅ |

---

## 🛒 MÓDULO: VENTAS

### Ubicación del código:
- **Archivo principal**: `apps/ventas/views.py`
- **Modelos**: `apps/ventas/models.py`
- **URLs**: `apps/ventas/urls.py`
- **Formularios**: `apps/ventas/forms.py`
- **Plantilla POS**: `templates/ventas/form.html`
- **Script frontend**: `static/js/ventas.js`

### Endpoints disponibles:

#### 1. **GET `/ventas/`** - Home de ventas
- **Ubicación**: `apps/ventas/views.py` línea ~
- **Autenticación**: Requerida
- **Roles permitidos**: Vendedor, Admin
- **Descripción**: Página de inicio del módulo ventas
- **Response**: Página HTML

#### 2. **GET `/ventas/nuevo/`** - Formulario de venta (POS)
- **Ubicación**: `apps/ventas/views.py` línea ~
- **Autenticación**: Requerida
- **Roles permitidos**: Vendedor, Admin
- **Descripción**: Carga la página con el POS (carrito de ventas)
- **Plantilla**: `templates/ventas/form.html`
- **Script**: `static/js/ventas.js`
- **Response**: 
  ```html
  - Productos en JSON embebido en: <script id="productos-data">
  - URLs de API en: <script id="ventas-js" data-url-crear-venta="..." data-url-lista-ventas="...">
  ```
- **Datos que recibe**:
  ```json
  {
    "productos_json": "[{pk: 1, fields: {nombre: 'Pan', precio: 1500, id: 1}}, ...]"
  }
  ```

#### 3. **POST `/ventas/nuevo/`** - Crear venta (API JSON)
- **Ubicación**: `apps/ventas/views.py` línea 40 (función `crear_venta`)
- **Autenticación**: Requerida
- **Roles permitidos**: Vendedor, Admin
- **Descripción**: Registra una venta con sus detalles
- **Content-Type**: `application/json`
- **Headers requeridos**: 
  ```
  X-CSRFToken: [token del servidor]
  Content-Type: application/json
  ```
- **Body (Request)**:
  ```json
  {
    "cliente_id": 1,
    "carrito": [
      {
        "id": 5,
        "nombre": "Pan Francés",
        "precio": 2000,
        "cantidad": 2,
        "descuento_pct": 0
      },
      {
        "id": 8,
        "nombre": "Croissant",
        "precio": 1500,
        "cantidad": 1,
        "descuento_pct": 10
      }
    ],
    "canal_venta": "TIENDA",
    "folio": "V-001"
  }
  ```
- **Response (Success)**:
  ```json
  {
    "status": "success",
    "venta_id": 42
  }
  ```
- **Response (Error)**:
  ```json
  {
    "status": "error",
    "message": "El carrito está vacío"
  }
  ```

#### 4. **GET `/ventas/listado/`** - Listar ventas
- **Ubicación**: `apps/ventas/views.py` línea 114 (función `lista_ventas`)
- **Autenticación**: Requerida
- **Roles permitidos**: Vendedor, Admin
- **Descripción**: Muestra historial de ventas realizadas
- **Plantilla**: `templates/ventas/lista_ventas.html`
- **Response**: Página HTML con tabla de ventas

#### 5. **GET `/ventas/editar/<venta_id>/`** - Editar venta
- **Ubicación**: `apps/ventas/views.py` línea 125 (función `editar_venta`)
- **Autenticación**: Requerida
- **Roles permitidos**: Vendedor, Admin
- **Descripción**: Permite modificar una venta existente

#### 6. **POST `/ventas/eliminar/<venta_id>/`** - Eliminar venta
- **Ubicación**: `apps/ventas/views.py` línea 155 (función `eliminar_venta`)
- **Autenticación**: Requerida
- **Roles permitidos**: Vendedor, Admin
- **Descripción**: Elimina una venta y devuelve el stock

#### 7. **GET `/ventas/comprobante/<venta_id>/`** - Ver comprobante
- **Autenticación**: Requerida
- **Descripción**: Muestra el comprobante de una venta en HTML
- **Plantilla**: `templates/ventas/comprobante.html`
- **Response**: Página HTML con detalles de la venta

---

## 📦 MÓDULO: INVENTARIO

### ⚠️ RESTRICCIÓN: Solo accesible para ADMINS
- **Protección**: `@user_passes_test(lambda u: u.is_superuser)` en `apps/inventario/views.py` líneas 28-29, 34-35

### Endpoints disponibles:

#### 1. **GET `/inventario/`** - Home inventario
- **Ubicación**: `apps/inventario/views.py` línea ~
- **Autenticación**: Requerida
- **Roles permitidos**: Solo Admin
- **Descripción**: Página principal de inventario

#### 2. **GET `/inventario/productos/`** - Listar productos
- **Ubicación**: `apps/inventario/views.py` línea 41 (función `lista_productos`)
- **Autenticación**: Requerida
- **Roles permitidos**: Solo Admin
- **Plantilla**: `templates/inventario/lista.html`
- **Parámetros de búsqueda**:
  - `q`: Texto para buscar en nombre
  - `categoria`: ID de categoría
  - `precio_min`: Precio mínimo
  - `precio_max`: Precio máximo
- **Response**: Página HTML con tabla de productos
- **Nota**: Usa `eliminado__isnull=True` para ocultar eliminados (línea 47)

#### 3. **GET/POST `/inventario/nuevo/`** - Crear producto
- **Ubicación**: `apps/inventario/views.py` línea 79 (función `crear_producto`)
- **Autenticación**: Requerida
- **Roles permitidos**: Solo Admin
- **Plantilla**: `templates/inventario/form.html`
- **GET Response**: Formulario HTML
- **POST Body**:
  ```json
  {
    "nombre": "Pan Integral",
    "descripcion": "Pan 100% integral",
    "marca": "Panadería X",
    "precio": "3500",
    "caducidad": "2025-12-15",
    "stock_actual": "25",
    "categorias": "1",
    "nutricional": "1"
  }
  ```

#### 4. **GET/POST `/inventario/editar/<id>/`** - Editar producto
- **Ubicación**: `apps/inventario/views.py` línea 90 (función `editar_producto`)
- **Autenticación**: Requerida
- **Roles permitidos**: Solo Admin
- **Plantilla**: `templates/inventario/form.html`
- **Similar a crear producto**

#### 5. **POST `/inventario/eliminar/<id>/`** - Eliminar producto
- **Ubicación**: `apps/inventario/views.py` línea 103 (función `eliminar_producto`)
- **Autenticación**: Requerida
- **Roles permitidos**: Solo Admin
- **Plantilla confirmación**: `templates/inventario/confirmar_eliminar.html`
- **Marca el producto como eliminado (soft delete)**
- **Nota**: Botón con clase `.btn-eliminar` dispara SweetAlert2 (ver `templates/base.html` línea ~)

#### 6. **GET `/inventario/categorias/`** - Listar categorías
- **Autenticación**: Requerida
- **Roles permitidos**: Solo Admin

#### 7. **POST `/inventario/categorias/nueva/`** - Crear categoría
- **Body**:
  ```json
  {
    "nombre": "Panes",
    "descripcion": "Panes frescos"
  }
  ```

---

## 📱 FLUJO DE VENTA (Frontend → Backend)

### 1. **Cargar página de ventas** (`/ventas/nuevo/`)
```
GET /ventas/nuevo/
↓
Backend obtiene: Productos NO eliminados
↓
Response: HTML + JSON de productos embebido
```

### 2. **El vendedor selecciona productos** (JavaScript en navegador)
```
Productos desde JSON embebido
↓ (Operaciones locales en JavaScript)
Carrito construido en memoria
(Sin llamadas al servidor)
```

### 3. **Vendedor hace clic en "Pagar"** (JavaScript)
```
fetch POST /ventas/nuevo/
Body: {carrito, cliente_id, ...}
Headers: X-CSRFToken
↓
Backend: Valida, crea Venta + DetalleVenta
↓
Response: {status: "success", venta_id: 42}
↓
JavaScript: Redirige a /ventas/listado/
```

---

## 🔑 Flujo de Autenticación

### Login
```
GET/POST /login/
Body: {username, password}
↓
Django valida credenciales
↓
Crea sesión + cookies
↓
Redirige a página de inicio (/)
```

### Logout
```
GET /logout/
↓
Destruye sesión
↓
Redirige a /login/
```

### CSRF
- **Token en**: Cada formulario `{% csrf_token %}`
- **Validación**: Automática en POST por middleware
- **Error**: Si falla, renderiza `csrf_failure.html` con SweetAlert

---

## 📊 Modelos de Base de Datos

### **Tabla: Productos**
```python
{
    "id": Integer (PK),
    "codigo": String (único, opcional),
    "nombre": String,
    "descripcion": String,
    "marca": String,
    "precio": Decimal(10,2),
    "caducidad": Date,
    "stock_actual": Integer,
    "categorias_id": Integer (FK),
    "nutricional_id": Integer (FK),
    "eliminado": DateTime (NULL si activo)
}
```

### **Tabla: Ventas**
```python
{
    "id": Integer (PK),
    "fecha": DateTime,
    "total_sin_iva": Decimal(10,2),
    "total_iva": Decimal(10,2),
    "total_con_iva": Decimal(10,2),
    "clientes_id": Integer (FK),
    "canal_venta": String,
    "folio": String,
    "monto_pagado": Decimal(10,2),
    "vuelto": Decimal(10,2)
}
```

### **Tabla: DetalleVenta**
```python
{
    "id": Integer (PK),
    "cantidad": Integer,
    "precio_unitario": Decimal(10,2),
    "descuento_pct": Decimal(5,2),
    "ventas_id": Integer (FK),
    "productos_id": Integer (FK)
}
```

### **Tabla: Clientes**
```python
{
    "id": Integer (PK),
    "rut": String,
    "nombre": String,
    "correo": String
}
```

---

## 🎨 Frontend - Archivos Importantes

### **ventas.js** (`/static/js/ventas.js`)
Maneja toda la lógica del carrito de ventas:
- Carga productos desde JSON embebido
- Permite agregar/quitar productos
- Calcula totales (neto, IVA, total)
- Envía carrito al servidor vía FETCH POST

**Funciones principales:**
- `renderProductos()` - Dibuja tarjetas de productos
- `agregarCarritoPorId(id)` - Agrega producto al carrito
- `renderCarrito()` - Actualiza tabla de carrito
- `calcularTotales()` - Calcula montos
- `btnPagar.onclick` - Envía venta al servidor

### **base.html** - Plantilla base
Incluye:
- Bootstrap 5
- SweetAlert2
- Navegación
- Block de contenido

### **form.html** (Ventas)
Plantilla del POS:
- Buscador de productos
- Tarjetas de productos
- Tabla de carrito
- Resumen de totales
- Botón de pago

---

## 🚀 Resumen: Cómo llama el Frontend al Backend

### Llamadas GET (Cargar páginas):
1. `/` - Inicio
2. `/login/` - Login
3. `/ventas/` - Home ventas
4. `/ventas/nuevo/` - POS (productos + carrito)
5. `/ventas/listado/` - Historial
6. `/inventario/` - Home inventario (solo admin)
7. `/inventario/productos/` - Lista productos (solo admin)

### Llamadas POST (Enviar datos):
1. **Venta**: `POST /ventas/nuevo/` (JSON)
   - Cliente: JavaScript (fetch)
   - Datos: Carrito, cliente_id

2. **Formularios**: `POST /inventario/nuevo/`, `POST /inventario/editar/<id>/`, etc.
   - Cliente: Formulario HTML tradicional
   - Datos: Form data

### Headers importantes:
```
X-CSRFToken: [Necesario en POST]
Content-Type: application/json [En llamadas API]
```

---

## 📝 Notas para el equipo de Frontend/Diseño

1. **No modifiques los atributos `data-*` de elementos**: Se usan en JavaScript
2. **Los IDs de elementos HTML son críticos**: Se referencian en `ventas.js`
3. **El JSON de productos viene embebido en el HTML**: En `<script id="productos-data">`
4. **Las URLs del API vienen en atributos del elemento `ventas-js`**
5. **Mantén los campos del formulario con los mismos `name`**: Django depende de ellos
6. **El CSRF token se obtiene de las cookies**: Automatizado en `ventas.js`

---

## 🧪 Ejemplo: Hacer una venta

### Step 1: GET `/ventas/nuevo/`
Obtiene la página con productos y formulario.

### Step 2: Usuario selecciona productos
JavaScript agrega al carrito local (sin servidor).

### Step 3: Usuario hace clic "Pagar"
```javascript
fetch('/ventas/nuevo/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': 'token_aqui'
  },
  body: JSON.stringify({
    carrito: [
      {id: 1, nombre: 'Pan', precio: 2000, cantidad: 2, descuento_pct: 0}
    ],
    cliente_id: 1
  })
})
.then(r => r.json())
.then(data => {
  if (data.status === 'success') {
    alert('Venta registrada!');
    window.location.href = '/ventas/listado/';
  }
})
```

### Step 4: Backend procesa
- Valida carrito
- Crea registro en BD
- Retorna `{status: 'success', venta_id: 42}`

### Step 5: Frontend redirige
Usuario ve el listado de ventas actualizado.

---

**¡Listo! Este documento explica todo lo que necesita saber el equipo de frontend/diseño sobre qué llama al backend y cómo.**
