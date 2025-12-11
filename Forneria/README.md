# 🥖 Sistema de Gestión Fornería

Sistema web completo para gestionar ventas e inventario de una panadería, con roles diferenciados para administradores y vendedores.

## 📋 Documentación Disponible

El proyecto incluye **4 documentos principales** que explican diferentes aspectos:

### 1. **DOCUMENTACION_API.md** 📚
Para **frontend/diseño y cualquier persona que necesite entender qué llama al backend**
- Endpoints disponibles
- Flujos de datos
- Modelos
- Ejemplos de requests/responses
- **Lectura recomendada: PRIMERO**

### 2. **GUIA_FRONTEND.md** 🎨
Para **diseñadores y developers de frontend**
- Qué elementos HTML son críticos
- Qué puedes cambiar sin romper nada
- Cómo cambiar estilos
- Checklist antes de subir cambios
- **Lectura recomendada: ANTES de hacer cambios**

### 3. **DOCUMENTACION_TECNICA.md** 🔧
Para **developers backend**
- Setup del proyecto
- Instalación de dependencias
- Testing
- Modelos y relaciones
- Transacciones
- Deployment
- **Lectura recomendada: PARA DESARROLLAR**

### 4. **ESTRUCTURA_BD.md** 🗄️
Para **anyone que necesite entender la BD**
- Diagrama de relaciones
- Esquema SQL detallado
- Queries útiles
- Constraints e índices
- **Lectura recomendada: CUANDO DUDES DE ESTRUCTURA**

---

## 🚀 Inicio Rápido

### 1. Clonar y configurar
```bash
git clone <repo>
cd Forneria
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

### 2. Crear base de datos
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 3. Crear cliente por defecto
```bash
python manage.py shell
>>> from apps.ventas.models import Clientes
>>> Clientes.objects.get_or_create(pk=1, defaults={'nombre': 'Varios'})
```

### 4. Ejecutar servidor
```bash
python manage.py runserver
```

### 5. Abrir en navegador
```
http://localhost:8000
```

---

## 👥 Roles y Acceso

| Usuario | Inventario | Ventas | Admin |
|---------|-----------|--------|-------|
| **Admin** | ✅ | ✅ | ✅ |
| **Vendedor** | ❌ | ✅ | ❌ |
| **Sin login** | ❌ | ❌ | ❌ |

### Crear vendedor:
```bash
python manage.py shell
>>> from django.contrib.auth.models import User, Group
>>> user = User.objects.create_user('vendedor1', 'email@test.com', 'pass123')
>>> group = Group.objects.get(name='Vendedor')
>>> user.groups.add(group)
```

---

## 📁 Estructura del Proyecto

```
Forneria/
├── Forneria/                 # Configuración Django
├── apps/
│   ├── inventario/          # CRUD de productos
│   └── ventas/              # Sistema de ventas (POS)
├── templates/               # HTML
├── static/                  # CSS, JS, Imágenes
├── DOCUMENTACION_API.md     # ← LEER PRIMERO
├── GUIA_FRONTEND.md         # Para diseñadores
├── DOCUMENTACION_TECNICA.md # Para backend
├── ESTRUCTURA_BD.md         # Base de datos
├── manage.py
└── requirements.txt
```

---

## 🔑 Conceptos Clave

### ✨ Las ventas NO restan stock automáticamente
- Las ventas solo registran transacciones
- El stock se maneja por `MovimientosInventario`
- Esto permite flexibilidad (devolver, ajustes manuales, etc.)

### 📦 Los productos con stock 0 SÍ aparecen en ventas
- Diseño intencional para flexibilidad
- Permite registrar ventas de productos "pronto a llegar"
- El vendedor ve que hay 0 stock pero puede vender

### 🗂️ Soft deletes en productos
- Los productos no se eliminan completamente
- Se marcan con `eliminado = NOW()`
- Esto permite auditoría y recuperación
- Las búsquedas filtra `WHERE eliminado IS NULL`

### 👤 Cliente por defecto "Varios"
- Venta sin cliente específico
- Se crea automáticamente (id=1)
- Todos los vendedores pueden usarlo

---

## 🔐 Seguridad Implementada

✅ **CSRF Protection**
- Token obligatorio en POST
- Validación automática del middleware
- Página amigable si falla (csrf_failure.html)

✅ **Autenticación por roles**
- Decoradores `@login_required`
- `@user_passes_test` para permisos específicos
- Admin vs Vendedor diferenciado

✅ **Validaciones en backend**
- Cantidad > 0
- Precio > 0
- Stock >= 0
- Clientes existentes

✅ **Transacciones atómicas**
- Si falla una venta, se revierte todo
- Integridad referencial garantizada

---

## 📞 Endpoints Principales

### 🔓 Públicos (pero requieren login)
```
GET  /                      → Inicio
GET  /login/                → Login
GET  /logout/               → Logout
```

### 🛒 Ventas (Vendedor + Admin)
```
GET  /ventas/               → Home
GET  /ventas/nuevo/         → POS
POST /ventas/nuevo/         → Crear venta (JSON)
GET  /ventas/listado/       → Historial
GET  /ventas/eliminar/<id>/ → Confirmar eliminar
POST /ventas/eliminar/<id>/ → Eliminar venta
```

### 📦 Inventario (Solo Admin)
```
GET  /inventario/           → Home
GET  /inventario/productos/ → Listar
GET  /inventario/nuevo/     → Crear
POST /inventario/nuevo/     → Guardar
GET  /inventario/editar/<id>/     → Editar
POST /inventario/editar/<id>/     → Guardar
POST /inventario/eliminar/<id>/   → Eliminar
```

---

## 💾 Base de Datos

Tablas principales:
- **producto** - Productos del negocio
- **venta** - Ventas realizadas
- **detalle_venta** - Líneas de cada venta
- **cliente** - Clientes
- **categoria** - Categorías de productos
- **nutricional** - Info nutricional de productos
- **movimientosinventario** - Entradas/salidas de stock

Ver `ESTRUCTURA_BD.md` para detalles completos.

---

## 🎨 Frontend

### Tecnología
- **HTML5** + Django Templates
- **CSS3** + Bootstrap 5
- **JavaScript** (Vanilla, no jQuery)
- **SweetAlert2** para alertas amigables

### Componentes principales
- **POS (Point of Sale)** en `/ventas/nuevo/`
  - Búsqueda de productos
  - Carrito dinámico
  - Cálculo de totales
  - Métodos de pago

### Archivos críticos
- `/static/js/ventas.js` - Lógica del carrito
- `/templates/ventas/form.html` - POS
- `/templates/base.html` - Plantilla base

---

## 🐛 Troubleshooting

### Error: "No Clientes matches the given query"
```bash
python manage.py shell
>>> from apps.ventas.models import Clientes
>>> Clientes.objects.get_or_create(pk=1, defaults={'nombre': 'Varios'})
```

### Error: Producto no aparece en ventas
- ✅ Verificar que `eliminado IS NULL`
- ✅ Verificar que sea admin si quieres editarlo
- ✅ Recargar página (F5) si cambió hace poco

### Error CSRF en POST
- ✅ Token se genera automáticamente
- ✅ Está en cookies (no envíes manualmente)
- ✅ Si falla, muestra página amigable

---

## 📝 Convenciones de Código

### Nombres de funciones
```python
# Vistas
crear_venta()      # GET/POST create
lista_ventas()     # GET list
editar_venta()     # GET/POST update
eliminar_venta()   # GET/POST delete
```

### Nombres de URLs (path names)
```python
name='crear_venta'
name='lista_ventas'
name='editar_venta'
```

### Variables de contexto
```python
# Templates reciben:
{'productos': [...], 'ventas': [...], 'form': ...}
```

---

## 🚀 Deployment

### Cambios requeridos:
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['tudominio.com']
SECRET_KEY = 'generar-nuevo-secret-key'
```

### Comandos:
```bash
python manage.py collectstatic
python manage.py check --deploy
python manage.py migrate
```

### Servir con Gunicorn:
```bash
pip install gunicorn
gunicorn Forneria.wsgi:application
```

---

## 📚 Recursos Adicionales

- [Django Documentation](https://docs.djangoproject.com/)
- [Bootstrap 5](https://getbootstrap.com/)
- [SweetAlert2](https://sweetalert2.github.io/)
- [Django Templates](https://docs.djangoproject.com/en/stable/topics/templates/)

---

## 👨‍💻 Contribuidores

- **Backend**: Django
- **Frontend**: HTML/CSS/JavaScript
- **Database**: MySQL/PostgreSQL

---

## 📄 Licencia

Proyecto de gestión para panadería. Uso interno.

---

## ❓ Preguntas Frecuentes

**P: ¿Dónde está la documentación?**
R: En `DOCUMENTACION_API.md` (lee primero)

**P: ¿Puedo cambiar los estilos?**
R: Sí, en `templates/` y `static/css/`. Lee `GUIA_FRONTEND.md`

**P: ¿Cómo hago una venta?**
R: Ve a `/ventas/nuevo/`, busca productos, agrega al carrito, paga.

**P: ¿Qué pasa si tengo un producto sin stock?**
R: Aparece igual en ventas. El vendedor ve que hay 0. Se puede vender igual.

**P: ¿Cómo controlo el stock?**
R: Vía `/inventario/movimientos/` (movimientos entrada/salida)

**P: ¿Puedo ver historial de ventas?**
R: Sí, en `/ventas/listado/`

---

## 🎯 Próximos pasos

1. **Lee**: `DOCUMENTACION_API.md`
2. **Setup**: Sigue "Inicio Rápido"
3. **Explora**: Abre `/ventas/nuevo/` y haz una venta de prueba
4. **Diseña**: Si eres frontend, lee `GUIA_FRONTEND.md`
5. **Desarrolla**: Si eres backend, lee `DOCUMENTACION_TECNICA.md`

---

**¡Cualquier duda, revisa la documentación relevante!** 📚
