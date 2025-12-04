from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Productos, Categorias, MovimientosInventario
from .forms import ProductoForm
from datetime import datetime

# =========================
# Funciones para roles
# =========================
def es_vendedor(user):
    return user.is_authenticated and user.groups.filter(name='Vendedor').exists()

def es_admin(user):
    return user.is_authenticated and user.is_superuser


# =========================
# LISTAR PRODUCTOS CON FILTROS AVANZADOS
# Solo usuarios autenticados pueden ver el inventario
# =========================
@login_required
def lista_productos(request):
    productos = Productos.objects.all()
    categorias = Categorias.objects.all()

    # Parámetros GET para filtros
    query = request.GET.get('q')
    categoria_id = request.GET.get('categoria')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    stock_min = request.GET.get('stock_min')
    stock_max = request.GET.get('stock_max')

    # Filtro por nombre
    if query:
        productos = productos.filter(nombre__icontains=query)

    # Filtro por categoría
    if categoria_id and categoria_id.isdigit():
        productos = productos.filter(categorias_id=categoria_id)

    # Filtro por rango de precios
    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)

    # Filtro por stock
    if stock_min:
        productos = productos.filter(stock_actual__gte=stock_min)
    if stock_max:
        productos = productos.filter(stock_actual__lte=stock_max)

    return render(request, 'inventario/lista.html', {
        'productos': productos,
        'categorias': categorias
    })


# =========================
# CREAR PRODUCTO
# Solo admin puede crear productos
# =========================
@login_required
@user_passes_test(es_admin)
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'inventario/form.html', {'form': form})


# =========================
# EDITAR PRODUCTO
# Solo admin puede editar productos
# =========================
@login_required
@user_passes_test(es_admin)
def editar_producto(request, pk):
    producto = get_object_or_404(Productos, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/form.html', {'form': form})


# =========================
# ELIMINAR PRODUCTO
# Solo admin puede eliminar productos
# =========================
@login_required
@user_passes_test(es_admin)
def eliminar_producto(request, pk):
    producto = get_object_or_404(Productos, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('lista_productos')
    return render(request, 'inventario/confirmar_eliminar.html', {'producto': producto})

# =========================
# MOVIMIENTOS DE INVENTARIO
# Solo admin puede registrar movimientos
# =========================
@login_required
@user_passes_test(es_admin)
def movimientos_inventario(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        action = request.POST.get('action')
        cantidad = int(request.POST.get('cantidad', 0))

        if producto_id and cantidad > 0:
            producto = get_object_or_404(Productos, pk=producto_id)
            
            # Registrar el movimiento
            MovimientosInventario.objects.create(
                productos=producto,
                tipo_movimiento=action,
                cantidad=cantidad,
                fecha=datetime.now()
            )

            # Actualizar stock
            if action == 'ingreso':
                producto.stock_actual += cantidad
            elif action == 'egreso':
                producto.stock_actual -= cantidad
            producto.save()

        return redirect('movimientos_inventario')

    productos = Productos.objects.all()
    movimientos = MovimientosInventario.objects.order_by('-fecha')[:10]
    return render(request, 'inventario/movimientos.html', {
        'productos': productos,
        'movimientos': movimientos
    })