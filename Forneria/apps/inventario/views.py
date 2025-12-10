# inventario/views.py
from decimal import Decimal

# Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.http import JsonResponse

# Local
from .models import Productos, Categorias, MovimientosInventario
from .forms import ProductoForm, CategoriaForm


# ============================================================
# ROLES / PERMISOS
# ============================================================
def es_vendedor(user):
    return user.is_authenticated and user.groups.filter(name='Vendedor').exists()

def es_admin(user):
    return user.is_authenticated and user.is_superuser


# ============================================================
# HOME
# ============================================================
@login_required
def inventario_home(request):
    return render(request, 'inventario/home.html')


# ============================================================
# PRODUCTOS — LISTAR + FILTROS
# ============================================================
@login_required
def lista_productos(request):
    productos = Productos.objects.all().select_related('categorias')
    categorias = Categorias.objects.all()

    # Filtros
    query = request.GET.get('q')
    categoria_id = request.GET.get('categoria')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    stock_min = request.GET.get('stock_min')
    stock_max = request.GET.get('stock_max')

    # Búsqueda
    if query:
        productos = productos.filter(nombre__icontains=query)

    # Filtro categoría
    if categoria_id and categoria_id.isdigit():
        productos = productos.filter(categorias_id=int(categoria_id))

    # Filtro precios
    try:
        if precio_min:
            productos = productos.filter(precio__gte=Decimal(precio_min))
        if precio_max:
            productos = productos.filter(precio__lte=Decimal(precio_max))
    except:
        pass

    # Filtro stock
    try:
        if stock_min:
            productos = productos.filter(stock_actual__gte=int(stock_min))
        if stock_max:
            productos = productos.filter(stock_actual__lte=int(stock_max))
    except:
        pass

    return render(request, 'inventario/lista.html', {
        'productos': productos,
        'categorias': categorias
    })


# ============================================================
# PRODUCTOS — CRUD (ADMIN)
# ============================================================
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


@login_required
@user_passes_test(es_admin)
def eliminar_producto(request, pk):
    producto = get_object_or_404(Productos, pk=pk)

    if request.method == 'POST':
        producto.delete()
        return redirect('lista_productos')

    return render(request, 'inventario/confirmar_eliminar.html', {'producto': producto})


# ============================================================
# CATEGORÍAS — CRUD
# ============================================================
@login_required
@user_passes_test(es_admin)
def lista_categorias(request):
    categorias = Categorias.objects.all()
    return render(request, 'inventario/lista_categorias.html', {'categorias': categorias})


@login_required
@user_passes_test(es_admin)
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()

    return render(request, 'inventario/form_categoria.html', {'form': form})


@login_required
@user_passes_test(es_admin)
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categorias, pk=pk)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, 'inventario/form_categoria.html', {'form': form})


@login_required
@user_passes_test(es_admin)
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categorias, pk=pk)

    if request.method == 'POST':
        categoria.delete()
        return redirect('lista_categorias')

    return render(request, 'inventario/confirmar_eliminar_categoria.html', {'categoria': categoria})


# ============================================================
# MOVIMIENTOS DE INVENTARIO
# ============================================================
@login_required
@user_passes_test(es_admin)
@transaction.atomic
def movimientos_inventario(request):

    # PROCESAR MOVIMIENTO
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        action = request.POST.get('action')

        try:
            cantidad = int(request.POST.get('cantidad', 0))
        except:
            cantidad = 0

        if not producto_id or cantidad <= 0:
            return redirect('movimientos_inventario')

        producto = Productos.objects.select_for_update().get(pk=producto_id)

        entrada = action in ('ingreso', 'ENTRADA', 'entrada')
        salida = action in ('egreso', 'SALIDA', 'salida')

        if entrada:
            MovimientosInventario.objects.create(
                productos=producto,
                tipo_movimiento=MovimientosInventario.ENTRADA,
                cantidad=cantidad,
                fecha=timezone.now()
            )
            producto.stock_actual = (producto.stock_actual or 0) + cantidad
            producto.save(update_fields=['stock_actual'])

        elif salida:
            stock_actual = producto.stock_actual or 0
            cantidad = min(cantidad, stock_actual)  # evita negativos

            MovimientosInventario.objects.create(
                productos=producto,
                tipo_movimiento=MovimientosInventario.SALIDA,
                cantidad=cantidad,
                fecha=timezone.now()
            )
            producto.stock_actual = F('stock_actual') - cantidad
            producto.save(update_fields=['stock_actual'])

        return redirect('movimientos_inventario')

    # LISTADO
    productos = Productos.objects.all().only('id', 'nombre', 'stock_actual')
    movimientos = MovimientosInventario.objects.select_related('productos').order_by('-fecha')[:10]

    return render(request, 'inventario/movimientos.html', {
        'productos': productos,
        'movimientos': movimientos
    })


# ============================================================
# API — JSON
# ============================================================
@login_required
def productos_json(request):
    productos = Productos.objects.filter(stock_actual__gt=0).values(
        'id', 'nombre', 'precio', 'stock_actual'
    )
    return JsonResponse(list(productos), safe=False)
