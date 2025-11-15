from django.shortcuts import render, redirect, get_object_or_404
from .models import Productos, Categorias, MovimientosInventario
from .forms import ProductoForm, CategoriaForm, MovimientoInventarioForm

# Listar productos con búsqueda
def lista_productos(request):
    productos = Productos.objects.all()
    query = request.GET.get('q')
    if query:
        productos = productos.filter(nombre__icontains=query)
    return render(request, 'inventario/lista.html', {'productos': productos})

# Crear producto
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'inventario/form.html', {'form': form})

# Editar producto
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

# Eliminar producto
def eliminar_producto(request, pk):
    producto = get_object_or_404(Productos, pk=pk)
    producto.delete()
    return redirect('lista_productos')
