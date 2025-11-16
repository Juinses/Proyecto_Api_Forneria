from django.shortcuts import render, redirect, get_object_or_404
from .models import Productos, Categorias
from .forms import ProductoForm

# Listar productos con búsqueda y filtros avanzados
def lista_productos(request):
    productos = Productos.objects.all()
    categorias = Categorias.objects.all()

    # Parámetros GET
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

    context = {
        'productos': productos,
        'categorias': categorias,
    }
    return render(request, 'inventario/lista.html', context)