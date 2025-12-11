# ⚡ Quick Reference - Desarrolladores

## 📍 Dónde ir rápidamente

**"Necesito entender qué hace el sistema"**
→ Lee `README.md` (resumen general)

**"Necesito entender los endpoints"**
→ Lee `DOCUMENTACION_API.md` (endpoints, requests, responses)

**"Voy a cambiar el diseño/HTML"**
→ Lee `GUIA_FRONTEND.md` (qué puedo tocar y qué no)

**"Voy a desarrollar backend"**
→ Lee `DOCUMENTACION_TECNICA.md` (setup, models, testing)

**"Necesito entender la BD"**
→ Lee `ESTRUCTURA_BD.md` (tablas, relaciones, queries)

---

## 🎯 Tareas Comunes

### Cambiar el color del botón "Pagar"
```html
<!-- En templates/ventas/form.html -->
<!-- Busca: -->
<button id="btnPagar" class="btn btn-success btn-lg">

<!-- Cambia a (ej: azul): -->
<button id="btnPagar" class="btn btn-primary btn-lg">
```

### Agregar un campo nuevo al formulario de venta
1. Agrega input en `templates/ventas/form.html`
2. Modifica `views.py` en `crear_venta()` para procesarlo
3. Actualiza el modelo `Ventas` si es necesario
4. Crea migration: `python manage.py makemigrations`

### Ver una venta en detalle
```
GET /ventas/listado/
(Haz click en una venta)
```

### Crear un producto nuevo (como admin)
```
GET /inventario/nuevo/
(Completa formulario)
POST /inventario/nuevo/
```

### Listar ventas filtradas (en backend)
```python
# En views.py
from django.db.models import Q

ventas = Ventas.objects.filter(
    Q(clientes__nombre__icontains='Juan') |
    Q(fecha__gte='2025-01-01')
).select_related('clientes').prefetch_related('detalles')
```

### Deshacer cambios accidentales
```bash
git checkout templates/ventas/form.html
git restore static/js/ventas.js
```

---

## 🔍 Debugging Rápido

### Ver qué productos hay en el carrito (en consola del navegador)
```javascript
console.log(carrito);
```

### Ver toda la lista de productos disponibles
```javascript
console.log(productos);
```

### Verificar que el token CSRF esté en cookies
```javascript
console.log(getCookie('csrftoken'));
```

### Ver el JSON que se envía al servidor
```javascript
// En ventas.js, antes de fetch, agrega:
console.log('Enviando:', JSON.stringify(data));
```

### Ver respuesta del servidor
```javascript
// En consola después de enviar
// El response se ve en Network → ver respuesta
```

---

## 🚀 Deploy Local para Pruebas

```bash
# Terminal 1: Servidor Django
python manage.py runserver

# Terminal 2: (Opcional) Python shell para testing
python manage.py shell
```

Abre: `http://localhost:8000`

---

## ⚙️ Settings Importantes

### `Forneria/settings.py`

```python
# Modo debug (CAMBIAR A FALSE EN PRODUCCIÓN)
DEBUG = True

# Base de datos actual
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

# Aplicaciones instaladas
INSTALLED_APPS = [
    'apps.inventario',
    'apps.ventas',
    # ...
]

# URLs a redirigir después de login
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

# Error personalizado CSRF
CSRF_FAILURE_VIEW = 'Forneria.views.csrf_failure'
```

---

## 🗂️ Archivos que Modificar Frecuentemente

### Para cambiar HTML/CSS:
```
templates/
├── base.html                    ← Encabezado, navegación
├── ventas/form.html             ← POS, carrito, botones
├── ventas/lista_ventas.html     ← Historial de ventas
└── inventario/                  ← Páginas de inventario

static/
├── css/                         ← Estilos CSS
│   ├── theme.css
│   ├── ventas.css
│   └── inventario.css
└── js/
    └── ventas.js                ← Lógica del carrito
```

### Para cambiar lógica backend:
```
apps/ventas/
├── views.py                     ← Endpoints POST/GET
├── models.py                    ← Modelos (Venta, DetalleVenta, Cliente)
├── forms.py                     ← Validaciones de formularios
└── urls.py                      ← Rutas

apps/inventario/
├── views.py                     ← CRUD productos
├── models.py                    ← Productos, Categorías, Nutricional
└── forms.py                     ← Validaciones
```

---

## 📊 Queries SQL Útiles (testing)

```sql
-- Ver todas las ventas
SELECT * FROM venta ORDER BY fecha DESC;

-- Ver detalles de una venta
SELECT dv.*, p.nombre FROM detalle_venta dv
JOIN producto p ON dv.producto_id = p.id
WHERE dv.venta_id = 1;

-- Ver total vendido hoy
SELECT SUM(total_con_iva) FROM venta 
WHERE DATE(fecha) = CURDATE();

-- Ver productos sin stock
SELECT * FROM producto 
WHERE stock_actual = 0 AND eliminado IS NULL;
```

---

## 🐛 Errores Comunes y Soluciones

| Error | Solución |
|-------|----------|
| "No Clientes" en venta | Crear cliente: `Clientes.objects.get_or_create(pk=1, defaults={'nombre': 'Varios'})` |
| 404 en `/inventario/` | Solo admins pueden acceder. Loguéate como superuser |
| 403 CSRF | Token no enviado o expiró. Recarga página (F5) |
| Productos no aparecen | Verificar que `eliminado IS NULL`. Recargar página. |
| JavaScript error en consola | Abrir F12 → Console. Ver error exacto. Revisar `ventas.js` |
| Variable no definida | Verificar que elemento HTML tiene el id correcto |

---

## 💾 Backup y Restore

```bash
# Exportar datos completos
python manage.py dumpdata > backup.json

# Importar datos
python manage.py loaddata backup.json

# Exportar solo ventas
python manage.py dumpdata apps.ventas > ventas_backup.json

# Exportar solo inventario
python manage.py dumpdata apps.inventario > inventario_backup.json
```

---

## 🔐 Crear usuarios de prueba

```bash
python manage.py shell
>>> from django.contrib.auth.models import User, Group
>>>
>>> # Admin
>>> admin = User.objects.create_user('admin', 'admin@test.com', 'admin123')
>>> admin.is_superuser = True
>>> admin.is_staff = True
>>> admin.save()
>>>
>>> # Vendedor
>>> vendedor = User.objects.create_user('vendedor1', 'vend@test.com', 'vend123')
>>> group = Group.objects.get(name='Vendedor')
>>> vendedor.groups.add(group)
>>>
>>> print("Admin: admin / admin123")
>>> print("Vendedor: vendedor1 / vend123")
```

---

## 🧪 Testear una venta completa (Python)

```python
# python manage.py shell
from apps.ventas.models import Clientes, Ventas, DetalleVenta
from apps.inventario.models import Productos
from decimal import Decimal

# 1. Obtener cliente
cliente = Clientes.objects.get(pk=1)

# 2. Obtener producto
producto = Productos.objects.first()

# 3. Crear venta
venta = Ventas.objects.create(
    clientes=cliente,
    total_sin_iva=Decimal('10000'),
    total_iva=Decimal('1900'),
    total_con_iva=Decimal('11900'),
    canal_venta='TIENDA'
)

# 4. Agregar detalle
DetalleVenta.objects.create(
    ventas=venta,
    productos=producto,
    cantidad=2,
    precio_unitario=Decimal('5000')
)

# 5. Ver resultado
print(f"Venta creada: {venta}")
print(f"Detalles: {venta.detalles.count()}")
print(f"Total: ${venta.total_con_iva}")
```

---

## 📱 Testear desde Postman/Thunder Client

```
POST http://localhost:8000/ventas/nuevo/
Headers:
  Content-Type: application/json
  X-CSRFToken: [obtener de cookies]

Body:
{
  "cliente_id": 1,
  "carrito": [
    {
      "id": 1,
      "nombre": "Pan",
      "precio": 2000,
      "cantidad": 2,
      "descuento_pct": 0
    }
  ],
  "canal_venta": "TIENDA"
}
```

---

## 🎯 Flujo típico de un desarrollador

1. **Setup inicial**
   ```bash
   git clone <repo>
   python -m venv venv
   source venv/Scripts/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   ```

2. **Crear dato de prueba**
   ```bash
   python manage.py shell
   # Crear cliente, productos, etc.
   ```

3. **Abrir en navegador**
   ```bash
   python manage.py runserver
   # http://localhost:8000
   ```

4. **Desarrollar**
   - Modifica archivos
   - Recarga página (F5)
   - Ver errores en consola (F12)

5. **Commit cambios**
   ```bash
   git add .
   git commit -m "Descripción"
   git push
   ```

---

## 📞 Stack Técnico Resumen

```
Frontend                Backend              Database
┌──────────────┐      ┌──────────────┐    ┌──────────────┐
│ HTML + Jinja │      │   Django 5   │    │   SQLite3    │
│ CSS + BS5    │      │   Python 3   │    │  (MySQL en   │
│ JavaScript   │◄────▶│ DRF (JSON)   │◄──▶│   producción)│
│ SweetAlert2  │      │ ORM Models   │    │              │
└──────────────┘      └──────────────┘    └──────────────┘
```

---

**Más info → Abre los otros archivos .md en la carpeta** 📚

