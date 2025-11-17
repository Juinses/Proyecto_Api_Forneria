from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Productos, Categorias
from .forms import ProductoForm

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
    producto.delete()
    return redirect('lista_productos')