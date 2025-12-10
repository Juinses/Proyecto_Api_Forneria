
# ventas/views.py
from decimal import Decimal
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.serializers import serialize

from .models import Ventas, Clientes, DetalleVenta
from apps.inventario.models import Productos

# =========================
# Roles
# =========================
def es_vendedor(user):
    return user.is_authenticated and user.groups.filter(name='Vendedor').exists()

def es_admin(user):
    return user.is_authenticated and user.is_superuser


@login_required
def ventas_home(request):
    return render(request, 'ventas/home.html')


# =========================
# Crear Venta (POST JSON)
# =========================
@login_required
@user_passes_test(lambda u: es_vendedor(u) or es_admin(u))
@transaction.atomic
def crear_venta(request):
    if request.method == 'POST':
        try:
            try:
                data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

            cliente_id = data.get('cliente_id') or 1  # Cliente "Varios" por defecto
            carrito = data.get('carrito', [])

            if not carrito:
                return JsonResponse({'status': 'error', 'message': 'El carrito está vacío'}, status=400)

            cliente = get_object_or_404(Clientes, pk=cliente_id)

            # Crear venta base; totales se recalculan después
            venta = Ventas.objects.create(
                clientes=cliente,
                descuento=Decimal('0.00'),
                canal_venta=data.get('canal_venta', 'TIENDA'),
                folio=data.get('folio')
            )

            for item in carrito:
                # Usa 'id' porque el modelo no tiene 'codigo'
                producto_id = item.get('id')
                try:
                    cantidad = int(item.get('cantidad', 0))
                    precio = Decimal(str(item.get('precio', '0.00')))
                except (TypeError, ValueError):
                    return JsonResponse({'status': 'error', 'message': 'Cantidad/precio inválidos'}, status=400)

                if cantidad <= 0 or precio < 0:
                    return JsonResponse({'status': 'error', 'message': 'Cantidad/precio inválidos'}, status=400)

                # Bloqueo por concurrencia
                producto = Productos.objects.select_for_update().get(pk=producto_id)
                stock_actual = producto.stock_actual or 0

                if cantidad > stock_actual:
                    return JsonResponse(
                        {'status': 'error', 'message': f"Stock insuficiente para {producto.nombre} (disp: {stock_actual})"},
                        status=400
                    )

                DetalleVenta.objects.create(
                    ventas=venta,
                    productos=producto,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    descuento_pct=item.get('descuento_pct')
                )

                # Update atómico del stock
                producto.stock_actual = F('stock_actual') - cantidad
                producto.save(update_fields=['stock_actual'])

            # Totales con Decimal y redondeo (IVA 19% por defecto)
            venta.recalcular_totales(iva_pct=Decimal('0.19'))

            # Pago completo opcional
            if data.get('pago_completo', True):
                venta.monto_pagado = venta.total_con_iva
                venta.vuelto = Decimal('0.00')
                venta.save(update_fields=['monto_pagado', 'vuelto'])

            return JsonResponse({'status': 'success', 'venta_id': venta.id})

        except Productos.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
        except Exception as e:
            # En producción, registra el error con logging
            return JsonResponse({'status': 'error', 'message': 'Error al crear la venta'}, status=500)

    # GET: render con productos disponibles
    productos = Productos.objects.filter(stock_actual__gt=0).only('id', 'nombre', 'precio')
    productos_json = serialize('json', productos, fields=('id', 'nombre', 'precio'))
    return render(request, 'ventas/form.html', {'productos_json': productos_json})


# =========================
# Listar Ventas
# =========================
@login_required
def lista_ventas(request):
    ventas = Ventas.objects.select_related('clientes').prefetch_related('detalles').order_by('-fecha')
    return render(request, 'ventas/lista_ventas.html', {'ventas': ventas})


# =========================
# Editar Venta (placeholder)
# =========================
@login_required
@user_passes_test(lambda u: es_vendedor(u) or es_admin(u))
@transaction.atomic
def editar_venta(request, venta_id):
    venta = get_object_or_404(Ventas.objects.select_for_update(), pk=venta_id)

    if request.method == 'POST':
        # TODO: Implementar edición con cálculo diferencial de stock
        return redirect('lista_ventas')

    productos = Productos.objects.filter(stock_actual__gt=0).only('id', 'nombre', 'precio')
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


# =========================
# Eliminar Venta
# =========================
@login_required
@user_passes_test(lambda u: es_vendedor(u) or es_admin(u))
@transaction.atomic
def eliminar_venta(request, venta_id):
    venta = get_object_or_404(Ventas.objects.select_for_update(), pk=venta_id)
    detalles = list(DetalleVenta.objects.filter(ventas=venta).select_related('productos'))

    if request.method == 'POST':
        # Devolver stock
        for detalle in detalles:
            producto = Productos.objects.select_for_update().get(pk=detalle.productos_id)
            producto.stock_actual = (producto.stock_actual or 0) + detalle.cantidad
            producto.save(update_fields=['stock_actual'])

        venta.delete()
        return redirect('lista_ventas')

    return render(request, 'ventas/confirmar_eliminar.html', {'venta': venta})


# =========================
# Comprobante (HTML)
# =========================
@login_required
def comprobante_html(request, venta_id):
    venta = get_object_or_404(Ventas, pk=venta_id)
    detalles = DetalleVenta.objects.filter(ventas=venta).select_related('productos')
    return render(request, 'ventas/comprobante.html', {
        'venta': venta,
        'detalles': detalles
    })


# =========================
# Comprobante (PDF)
# =========================
@login_required
def comprobante_pdf(request, venta_id):
    from weasyprint import HTML

    venta = get_object_or_404(Ventas, pk=venta_id)
    detalles = DetalleVenta.objects.filter(ventas=venta).select_related('productos')

    html_string = render_to_string('ventas/comprobante.html', {
        'venta': venta,
        'detalles': detalles
    })

    # base_url para rutas de CSS/imagenes
    base_url = request.build_absolute_uri('/')
    pdf_bytes = HTML(string=html_string, base_url=base_url).write_pdf()

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=comprobante_{venta_id}.pdf'
    return response

def lista_clientes(request):
    return render(request, 'ventas/clientes_list.html')
