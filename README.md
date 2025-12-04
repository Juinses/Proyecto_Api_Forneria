Forneria – Backend Django

Descripción del Proyecto
Este proyecto implementa el backend para el sistema Forneria, dividido en dos módulos principales:

- Inventario Gestión de productos, categorías y movimientos.
- Ventas: Registro de ventas, cálculo de totales, descuentos y actualización de stock.

El proyecto está desarrollado eDjango y conectado a una base de datos MySQL existente.

---

Estructura del Proyecto
```
Forneria/
│
├── apps/
│   ├── inventario/
│   │   ├── admin.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   ├── views.py
│   ├── ventas/
│       ├── admin.py
│       ├── forms.py
│       ├── models.py
│       ├── urls.py
│       ├── views.py
│
├── templates/   # (si se usan vistas con HTML)
├── static/
├── manage.py
├── requirements.txt
└── README.md
```

---

Configuración Inicial
1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar base de datos en `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nombre_bd',
        'USER': 'usuario',
        'PASSWORD': 'contraseña',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

3. Ejecutar migraciones:
```bash
python manage.py migrate
```

4. Crear superusuario:
```bash
python manage.py createsuperuser
```

---

Módulo Inventario
Modelos
- `Productos`: nombre, precio, caducidad, stock, categoría, nutricional.
- `Categorias`: nombre, descripción.
- `MovimientosInventario`: tipo_movimiento, cantidad, fecha, producto.
Funcionalidades
- CRUD completo para productos y categorías.
- Búsqueda por nombre.
- Gestión desde Django Admin.

Archivos clave
- `forms.py`: Formularios para Productos, Categorías y Movimientos.
- `views.py`: Vistas para listar, crear, editar y eliminar productos.
- `urls.py`: Rutas del módulo.

---

Módulo Ventas
Modelos
- `Ventas`: fecha, totales (sin IVA, IVA, con IVA), descuento, cliente.
- `Clientes`: rut, nombre, correo.
- `DetalleVenta`: producto, cantidad, precio_unitario, descuento_pct.

Funcionalidades
- CRUD para ventas y clientes.
- Lógica de negocio:
  - Cálculo automático de totales.
  - Aplicación de descuentos.
  - Actualización de stock en Inventario.
  - Validación de stock disponible.

Código clave (crear venta con lógica)
```python
@transaction.atomic
def crear_venta(request):
    if request.method == 'POST':
        venta_form = VentaForm(request.POST)
        detalle_form = DetalleVentaForm(request.POST)

        if venta_form.is_valid() and detalle_form.is_valid():
            venta = venta_form.save(commit=False)
            cantidad = detalle_form.cleaned_data['cantidad']
            producto = detalle_form.cleaned_data['productos']
            precio_unitario = detalle_form.cleaned_data['precio_unitario']
            descuento_pct = detalle_form.cleaned_data.get('descuento_pct', 0)

            if cantidad > producto.stock_actual:
                venta_form.add_error(None, f"Stock insuficiente para {producto.nombre}")
                return render(request, 'ventas/form.html', {'venta_form': venta_form, 'detalle_form': detalle_form})

            subtotal = cantidad * precio_unitario
            total_sin_iva = subtotal
            total_iva = round(total_sin_iva * 0.19, 2)
            descuento = round((subtotal * descuento_pct) / 100, 2)
            total_con_iva = total_sin_iva + total_iva - descuento

            venta.total_sin_iva = total_sin_iva
            venta.total_iva = total_iva
            venta.descuento = descuento
            venta.total_con_iva = total_con_iva
            venta.save()

            detalle = detalle_form.save(commit=False)
            detalle.ventas = venta
            detalle.save()

            producto.stock_actual -= cantidad
            producto.save()

            return redirect('lista_ventas')
```

---

Roles y Permisos
- Administrador: acceso completo.
- Vendedor: solo registrar ventas y consultar productos.

---

Próximos pasos
- Implementar filtros avanzados en Inventario.
- Generar comprobantes (HTML/PDF) para Ventas.
- Integrar autenticación y permisos.
- Pruebas unitarias y documentación adicional.

python manage.py inspectdb > models.py
este comando sirve para bajar los modelos directos de la base de datos es util cuando
ya se cuenta con una base de datos creada