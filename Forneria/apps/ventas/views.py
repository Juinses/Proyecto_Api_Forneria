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
@transaction.atomic
def crear_venta(request):
    if request.method == 'POST':
        # Leer JSON del POS
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

        cliente_id = data.get('cliente_id', 1)  # Cliente default "Varios"
        carrito = data.get('carrito', [])

        if not carrito:
            return JsonResponse({'status': 'error', 'message': 'El carrito está vacío'}, status=400)

        # Obtener o crear cliente por defecto
        cliente, _ = Clientes.objects.get_or_create(
            pk=cliente_id,
            defaults={'nombre': 'Varios', 'rut': None}
        )

        # Crear venta inicial (totales en 0, luego se recalculan con el modelo)
        venta = Ventas.objects.create(
            clientes=cliente,
            descuento=Decimal('0.00'),
            canal_venta=data.get('canal_venta', 'TIENDA'),
            folio=data.get('folio'),
        )

        # Crear detalle producto x producto
        for item in carrito:
            producto_id = item.get('id')
            try:
                producto = Productos.objects.select_for_update().get(pk=producto_id)
            except Productos.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': f"Producto con ID '{producto_id}' no encontrado"}, status=400)

            cantidad = int(item.get('cantidad', 0))
            precio = Decimal(str(item.get('precio', '0.00')))

            if cantidad <= 0 or precio <= 0:
                return JsonResponse({'status': 'error', 'message': 'Cantidad o precio inválidos'}, status=400)

            # Stock validado y descontado automáticamente en models.save()
            DetalleVenta.objects.create(
                ventas=venta,
                productos=producto,
                cantidad=cantidad,
                precio_unitario=precio,
                descuento_pct=item.get('descuento_pct'),
            )

        # Recalcular totales usando método del modelo
        venta.recalcular_totales()

        # Si es pago completo:
        if data.get('pago_completo', True):
            venta.monto_pagado = venta.total_con_iva
            venta.vuelto = Decimal('0.00')
            venta.save(update_fields=['monto_pagado', 'vuelto'])

        return JsonResponse({'status': 'success', 'venta_id': venta.id})

    # Método GET: pasar productos al POS
    productos = Productos.objects.filter(eliminado__isnull=True).only('id', 'nombre', 'precio')
    productos_json = serialize('json', productos, fields=('id', 'nombre', 'precio'))
    return render(request, 'ventas/form.html', {'productos_json': productos_json})

def lista_clientes(request):
    return HttpResponse("Lista de clientes (placeholder)")

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
