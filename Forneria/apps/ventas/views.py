# ventas/views.py
from decimal import Decimal
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.serializers import serialize

from .models import Ventas, Clientes, DetalleVenta
from apps.inventario.models import Productos
from .forms import ClienteForm


# -------------------------
# Roles
# -------------------------
def es_vendedor(user):
    return user.is_authenticated and user.groups.filter(name='Vendedor').exists()

def es_admin(user):
    return user.is_authenticated and user.is_superuser


# -------------------------
# Home
# -------------------------
@login_required
def ventas_home(request):
    return render(request, 'ventas/home.html')


# -------------------------
# Crear Venta (JSON)
# -------------------------
@login_required
@user_passes_test(lambda u: es_vendedor(u) or es_admin(u))
def crear_venta(request):
    if request.method == 'POST':
        import json
        from decimal import Decimal
        from django.http import JsonResponse
        from apps.ventas.models import Ventas

        # Leer JSON del POS
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

        cliente_id = data.get('cliente_id')
        if not cliente_id:
            return JsonResponse({'status': 'error', 'message': 'Debes seleccionar un cliente'}, status=400)

        try:
            cliente = Clientes.objects.get(pk=cliente_id)
        except Clientes.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Cliente no encontrado'}, status=400)

        # Crear venta mínima
        venta = Ventas.objects.create(
            clientes=cliente,
            descuento=Decimal('0.00'),
            canal_venta='TIENDA',
        )

        return JsonResponse({'status': 'success', 'venta_id': venta.id})

    # GET → mostrar formulario con productos y clientes
    productos = Productos.objects.all()
    productos_json = serialize('json', productos, fields=('id', 'nombre', 'precio'))

    clientes = Clientes.objects.all()

    return render(request, 'ventas/form.html', {
        'productos_json': productos_json,
        'clientes': clientes
    })

# -------------------------
# Lista clientes (para modal)
# ------------------------- 
def lista_clientes(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda en la base de datos
            return redirect('lista_clientes')  # Recarga la misma página para actualizar la lista
    else:
        form = ClienteForm()

    clientes = Clientes.objects.all()
    return render(request, "ventas/clientes_list.html", {
        "clientes": clientes,
        "form": form
    })

# -------------------------
# Lista ventas
# -------------------------
@login_required
def lista_ventas(request):
    ventas = Ventas.objects.select_related('clientes').prefetch_related('detalles').order_by('-fecha')
    return render(request, 'ventas/lista_ventas.html', {'ventas': ventas})


# -------------------------
# Editar venta (simple)
# -------------------------
@login_required
@user_passes_test(lambda u: es_vendedor(u) or es_admin(u))
@transaction.atomic
def editar_venta(request, venta_id):
    venta = get_object_or_404(Ventas.objects.select_for_update(), pk=venta_id)

    if request.method == 'POST':
        return redirect('lista_ventas')

    productos = Productos.objects.filter(eliminado__isnull=True).only('id', 'nombre', 'precio')
    productos_json = serialize('json', productos, fields=('id', 'nombre', 'precio'))

    detalles = DetalleVenta.objects.filter(ventas=venta).select_related('productos')
    carrito = [{
        'id': d.productos.id,
        'nombre': d.productos.nombre,
        'precio': float(d.precio_unitario),
        'cantidad': d.cantidad
    } for d in detalles]

    return render(request, 'ventas/form.html', {
        'productos_json': productos_json,
        'venta': venta,
        'carrito_json': json.dumps(carrito)
    })


# -------------------------
# Eliminar venta: devolver stock
# -------------------------
@login_required
@user_passes_test(lambda u: es_vendedor(u) or es_admin(u))
@transaction.atomic
def eliminar_venta(request, venta_id):
    venta = get_object_or_404(Ventas.objects.select_for_update(), pk=venta_id)
    detalles = DetalleVenta.objects.filter(ventas=venta).select_related('productos')

    if request.method == 'POST':
        # Devolver stock
        for d in detalles:
            producto = Productos.objects.select_for_update().get(pk=d.productos_id)
            producto.stock_actual += d.cantidad
            producto.save(update_fields=['stock_actual'])

        venta.delete()
        return redirect('lista_ventas')

    return render(request, 'ventas/confirmar_eliminar.html', {'venta': venta})


# -------------------------
# Comprobante HTML
# -------------------------
@login_required
def comprobante_html(request, venta_id):
    venta = get_object_or_404(Ventas, pk=venta_id)
    detalles = DetalleVenta.objects.filter(ventas=venta).select_related('productos')
    return render(request, 'ventas/comprobante.html', {'venta': venta, 'detalles': detalles})


# -------------------------
# Comprobante PDF
# -------------------------
@login_required
def comprobante_pdf(request, venta_id):
    from weasyprint import HTML

    venta = get_object_or_404(Ventas, pk=venta_id)
    detalles = DetalleVenta.objects.filter(ventas=venta).select_related('productos')

    html_string = render_to_string('ventas/comprobante.html', {'venta': venta, 'detalles': detalles})
    pdf_bytes = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=comprobante_{venta_id}.pdf'
    return response
