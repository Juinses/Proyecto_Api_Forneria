# 🔧 Guía Técnica - Desarrollo Backend

## Instalación y Setup

### 1. Crear entorno virtual
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# o
source venv/bin/activate  # Linux/Mac
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Crear superuser
```bash
python manage.py createsuperuser
```

### 5. Crear grupos de permisos
```bash
python manage.py shell
>>> from django.contrib.auth.models import Group
>>> Group.objects.create(name='Vendedor')
>>> Group.objects.create(name='Admin')
```

### 6. Crear cliente por defecto
```bash
python manage.py shell
>>> from apps.ventas.models import Clientes
>>> Clientes.objects.get_or_create(pk=1, defaults={'nombre': 'Varios'})
```

### 7. Ejecutar servidor
```bash
python manage.py runserver
```

---

## Estructura de Archivos Críticos

### `Forneria/settings.py`
Configuraciones Django principales:
- `DEBUG = True` - Cambiar a False en producción
- `ALLOWED_HOSTS = []` - Agregar dominios en producción
- `CSRF_FAILURE_VIEW = 'Forneria.views.csrf_failure'` - Error CSRF personalizado
- `LOGIN_URL = '/login/'` - Redireccionamiento login
- `INSTALLED_APPS` - Apps instaladas
- `MIDDLEWARE` - Middleware de Django

### `Forneria/urls.py`
Rutas principales:
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(...), name='login'),
    path('logout/', auth_views.LogoutView.as_view(...), name='logout'),
    path('inventario/', include('apps.inventario.urls')),
    path('ventas/', include('apps.ventas.urls')),
]
```

### `apps/ventas/views.py`
Funciones principales (con números de línea):
- `crear_venta(request)` **Línea 40** - POST JSON con carrito
- `lista_ventas(request)` **Línea 114** - GET lista de ventas
- `editar_venta(request, venta_id)` **Línea 125** - GET/POST editar venta
- `eliminar_venta(request, venta_id)` **Línea 155** - POST eliminar (devuelve stock)

**Conexión con modelos**: `apps/ventas/models.py`
- Modelo `Ventas`: Tabla principal de ventas
- Modelo `DetalleVenta`: Items de cada venta
- Modelo `Clientes`: Información del cliente

### `apps/inventario/views.py`
Funciones principales (con números de línea):
- `lista_productos(request)` **Línea 41** - GET con filtros (solo admin)
- `crear_producto(request)` **Línea 79** - GET/POST crear producto
- `editar_producto(request, pk)` **Línea 90** - GET/POST editar producto
- `eliminar_producto(request, pk)` **Línea 103** - POST eliminar (soft delete)

**Protección de rutas**: Todas protegidas con `@user_passes_test(lambda u: u.is_superuser)` (**Líneas 28-29, 34-35**)

**Conexión con modelos**: `apps/inventario/models.py`
- Modelo `Productos`: Tabla de productos
- Modelo `Categorias`: Categorías de productos
- Modelo `Nutricional`: Información nutricional (ForeignKey, no OneToOne)

---

## Modelos Django

### Relaciones:
```
Productos (M) -----> (1) Nutricional  (múltiples productos pueden compartir info nutricional)
Productos (M) ----> (1) Categorias

Ventas (1) -----> (M) DetalleVenta
Ventas (M) -----> (1) Clientes

DetalleVenta -----> Productos
DetalleVenta -----> Ventas
```

### Validaciones importantes:
- `Productos.stock_actual >= 0` (CheckConstraint)
- `Productos.stock_minimo <= stock_maximo`
- `Productos.caducidad >= elaboracion`
- `DetalleVenta.cantidad >= 1`

---

## Lógica de Negocio

### Crear una venta:
1. Cliente selecciona productos en frontend (JavaScript)
2. Frontend envía POST a `/ventas/nuevo/` con JSON
3. Backend:
   - Valida cliente existe (o lo crea)
   - Por cada item en carrito:
     - Busca producto por ID
     - Valida cantidad > 0 y precio > 0
     - Crea DetalleVenta
     - **NO** resta stock (se maneja por movimientos)
   - Calcula totales usando `Venta.recalcular_totales()`
   - Retorna `{status: 'success', venta_id: X}`
4. Frontend redirige a listado

### Eliminar una venta:
1. GET `/ventas/eliminar/<venta_id>/` - Muestra confirmación
2. POST `/ventas/eliminar/<venta_id>/` - Ejecuta
3. Backend:
   - Obtiene todos los DetalleVenta de la venta
   - **Devuelve stock** a cada producto
   - Elimina la venta

### Stock en inventario:
- Movimientos se manejan por `MovimientosInventario`
- `Productos.stock_actual` se actualiza manualmente
- Las ventas **NO** restan stock automáticamente

---

## Decoradores y Permisos

### `@login_required`
Redirige a login si no está autenticado.

### `@user_passes_test(lambda u: u.is_superuser)`
Solo superusers pueden acceder.

### `@user_passes_test(lambda u: es_vendedor(u) or es_admin(u))`
Vendedores y admins pueden acceder.

### Funciones helpers:
```python
def es_vendedor(user):
    return user.is_authenticated and user.groups.filter(name='Vendedor').exists()

def es_admin(user):
    return user.is_authenticated and user.is_superuser
```

---

## Serialización JSON

### Django serialize():
Devuelve formato:
```json
[
  {
    "pk": 1,
    "fields": {
      "nombre": "Pan",
      "precio": "2000.00",
      "id": 1
    }
  }
]
```

Frontend normaliza esto en `ventas.js`:
```javascript
const productos = rawProductos.map(p => ({
    id: p.pk,
    nombre: p.fields.nombre,
    precio: Number(p.fields.precio)
}));
```

---

## Notificaciones Frontend (SweetAlert2)

### Configuración:
- Librería cargada en `templates/base.html`
- Disponible globalmente en todas las páginas
- No requiere configuración adicional

### Usos automáticos:
```javascript
// En ventas.js - Función reutilizable
function mostrarNotificacion(titulo, mensaje, tipo = 'info') {
    Swal.fire({
        title: titulo,
        text: mensaje,
        icon: tipo, // 'success', 'error', 'warning', 'info'
        confirmButtonText: 'Aceptar',
        confirmButtonColor: '#0d6efd'
    });
}
```

### Tipos de notificación:
- `'success'` - Verde (operación exitosa)
- `'error'` - Rojo (error)
- `'warning'` - Amarillo (advertencia)
- `'info'` - Azul (información)

### Confirmaciones automáticas:
En `base.html` hay un script que convierte botones con clase `.btn-eliminar` en confirmaciones SweetAlert:
```html
<a href="/inventario/eliminar/1/" class="btn-eliminar" data-mensaje="¿Eliminar?">
    <i class="bi bi-trash"></i>
</a>
```

### Cómo agregar notificaciones en nuevo código:
```python
# En views.py
from django.contrib import messages

messages.success(request, 'Operación exitosa!')
messages.error(request, 'Error al procesar')
messages.warning(request, 'Advertencia')
```

O en JavaScript:
```javascript
mostrarNotificacion("Título", "Mensaje aquí", "success");
```

---

## Transacciones

### `@transaction.atomic`
Decorator para operaciones que deben ser atómicas.

Usado en:
- `crear_venta()` - Si falla, no se guarda nada
- `editar_venta()`
- `movimientos_inventario()`

---

## CSRF Protection

### Token generado:
```html
{% csrf_token %}  <!-- En formularios -->
```

### En JSON POST:
Frontend obtiene token de cookies:
```javascript
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie) {
        document.cookie.split(';').forEach(cookie => {
            if (cookie.trim().startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            }
        });
    }
    return cookieValue;
}
```

Envía en headers:
```javascript
headers: {
    'X-CSRFToken': getCookie('csrftoken'),
    'Content-Type': 'application/json'
}
```

---

## Errores comunes

### Error: "No Clientes matches the given query"
**Causa**: Cliente con ID 1 no existe.
**Solución**: Crear cliente por defecto:
```bash
python manage.py shell
>>> from apps.ventas.models import Clientes
>>> Clientes.objects.get_or_create(pk=1, defaults={'nombre': 'Varios'})
```

### Error: "Producto con ID 'X' no encontrado"
**Causa**: El producto fue eliminado o no existe.
**Solución**: Verificar que `eliminado IS NULL` en la query.

### Error CSRF
**Causa**: Token expirado o no enviado.
**Solución**: El middleware muestra página personalizada `csrf_failure.html`.

---

## Endpoints JSON Disponibles

### POST `/ventas/nuevo/`
```json
REQUEST:
{
  "cliente_id": 1,
  "carrito": [
    {"id": 5, "nombre": "Pan", "precio": 2000, "cantidad": 2, "descuento_pct": 0}
  ],
  "canal_venta": "TIENDA",
  "folio": "V-001"
}

RESPONSE (Success):
{
  "status": "success",
  "venta_id": 42
}

RESPONSE (Error):
{
  "status": "error",
  "message": "Descripción del error"
}
```

---

## Testing

### Test de venta simple:
```python
# En terminal interactiva
python manage.py shell

>>> from apps.ventas.models import Clientes, Ventas, DetalleVenta
>>> from apps.inventario.models import Productos
>>> 
>>> # Crear cliente
>>> cliente = Clientes.objects.get_or_create(pk=1, defaults={'nombre': 'Varios'})[0]
>>> 
>>> # Crear producto
>>> producto = Productos.objects.first()
>>> 
>>> # Crear venta
>>> venta = Ventas.objects.create(
...     clientes=cliente,
...     total_sin_iva=10000,
...     total_iva=1900,
...     total_con_iva=11900
... )
>>> 
>>> # Crear detalle
>>> DetalleVenta.objects.create(
...     ventas=venta,
...     productos=producto,
...     cantidad=2,
...     precio_unitario=5000
... )
>>> 
>>> print(venta)
Venta #1 - Varios
```

---

## Producción

### Cambios requeridos en `settings.py`:
```python
DEBUG = False
ALLOWED_HOSTS = ['tudominio.com', 'www.tudominio.com']
SECRET_KEY = 'generar-nueva-clave-segura'
```

### Comandos previos al deploy:
```bash
python manage.py collectstatic
python manage.py check --deploy
python manage.py migrate
python manage.py createsuperuser
```

### Servir con Gunicorn:
```bash
pip install gunicorn
gunicorn Forneria.wsgi:application --bind 0.0.0.0:8000
```

---

## Variables de Entorno Recomendadas

```bash
# .env
DEBUG=False
SECRET_KEY=tu-clave-segura-aqui
DB_ENGINE=django.db.backends.postgresql
DB_NAME=forneria_db
DB_USER=usuario
DB_PASSWORD=contraseña
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
```

---

## Logs y Debugging

### Habilitar logging:
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Uso en vistas:
```python
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Creando venta para cliente {cliente_id}")
logger.error(f"Error al procesar carrito: {error}")
```

---

**Documentación completada. ¡Cualquier duda, consulta este archivo!**
