from decimal import Decimal

# Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.http import JsonResponse
from .forms import CategoriaForm

# Local
from .models import Productos, Categorias, MovimientosInventario, Nutricional
from .forms import ProductoForm, CategoriaForm, NutricionalForm


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
@user_passes_test(lambda u: u.is_superuser, login_url='/')
def inventario_home(request):
    return render(request, 'inventario/home.html')


# ============================================================
# PRODUCTOS — LISTADO + FILTROS
# ============================================================
@login_required
@user_passes_test(lambda u: u.is_superuser, login_url='/')
def lista_productos(request):
    productos = Productos.objects.select_related('categorias').all()
    categorias = Categorias.objects.all()

    q = request.GET.get('q')
    cat = request.GET.get('categoria')
    pmin = request.GET.get('precio_min')
    pmax = request.GET.get('precio_max')
    smin = request.GET.get('stock_min')
    smax = request.GET.get('stock_max')

    if q:
        productos = productos.filter(nombre__icontains=q)

    if cat and cat.isdigit():
        productos = productos.filter(categorias_id=int(cat))

    if pmin:
        productos = productos.filter(precio__gte=Decimal(pmin))
    if pmax:
        productos = productos.filter(precio__lte=Decimal(pmax))

    if smin:
        productos = productos.filter(stock_actual__gte=int(smin))
    if smax:
        productos = productos.filter(stock_actual__lte=int(smax))

    return render(request, 'inventario/lista.html', {
        'productos': productos,
        'categorias': categorias,
    })


# ============================================================
# PRODUCTOS — CRUD
# ============================================================
@login_required
@user_passes_test(es_admin)
def crear_producto(request):
    form = ProductoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('lista_productos')

    return render(request, 'inventario/form.html', {'form': form})


@login_required
@user_passes_test(es_admin)
def editar_producto(request, pk):
    producto = get_object_or_404(Productos, pk=pk)
    form = ProductoForm(request.POST or None, instance=producto)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('lista_productos')

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
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            # Siempre devolver JSON si es AJAX
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "id": categoria.id,
                    "nombre": categoria.nombre
                })
            # En caso normal, recargar la misma página
            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = CategoriaForm()

    return render(request, "inventario/categorias/form.html", {"form": form})

@login_required
@user_passes_test(es_admin)
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categorias, pk=pk)
    form = CategoriaForm(request.POST or None, instance=categoria)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('lista_categorias')

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
# Creacion Nutricional
# ============================================================
@login_required
@user_passes_test(es_admin)
def crear_nutricional(request):
    if request.method == "POST":
        form = NutricionalForm(request.POST)
        if form.is_valid():
            nutricional = form.save()
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "id": nutricional.id,
                    "nombre": str(nutricional)
                })
            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = NutricionalForm()
    return render(request, "inventario/nutricional/form.html", {"form": form})
# ============================================================
# MOVIMIENTOS DE INVENTARIO
# ============================================================
@login_required
@user_passes_test(es_admin)
@transaction.atomic
def movimientos_inventario(request):

    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        action = request.POST.get('action')
        cantidad = int(request.POST.get('cantidad', 0))

        if not producto_id or cantidad <= 0:
            return redirect('movimientos_inventario')

        producto = Productos.objects.select_for_update().get(pk=producto_id)

        if action.lower() in ('ingreso', 'entrada'):
            MovimientosInventario.objects.create(
                productos=producto,
                tipo_movimiento=MovimientosInventario.ENTRADA,
                cantidad=cantidad
            )
            producto.stock_actual = (producto.stock_actual or 0) + cantidad

        elif action.lower() in ('egreso', 'salida'):
            cantidad = min(cantidad, producto.stock_actual or 0)
            MovimientosInventario.objects.create(
                productos=producto,
                tipo_movimiento=MovimientosInventario.SALIDA,
                cantidad=cantidad
            )
            producto.stock_actual = F('stock_actual') - cantidad

        producto.save(update_fields=['stock_actual'])
        return redirect('movimientos_inventario')

    productos = Productos.objects.only('id', 'nombre', 'stock_actual')
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
