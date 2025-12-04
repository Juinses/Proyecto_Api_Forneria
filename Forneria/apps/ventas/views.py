from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
import tempfile
import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.serializers import serialize


from .models import Ventas, Clientes, DetalleVenta
from apps.inventario.models import Productos
from .forms import VentaForm, DetalleVentaForm

# =========================
# Funciones para roles
# =========================
def es_vendedor(user):
    return user.is_authenticated and user.groups.filter(name='Vendedor').exists()

def es_admin(user):
    return user.is_authenticated and user.is_superuser


# =========================
# REGISTRAR VENTA CON LÓGICA DE NEGOCIO
# Solo vendedores y admin pueden crear ventas
# =========================
@login_required
@user_passes_test(lambda u: es_vendedor(u) or es_admin(u))
@transaction.atomic
def crear_venta(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cliente_id = data.get('cliente_id', 1) # Usar cliente "Varios" por defecto
            carrito = data.get('carrito', [])

            if not carrito:
                return JsonResponse({'status': 'error', 'message': 'El carrito está vacío'}, status=400)

            cliente = get_object_or_404(Clientes, pk=cliente_id)
            
            # Calcular totales
            neto = sum(item['precio'] * item['cantidad'] for item in carrito)
            iva = round(neto * 0.19)
            total = neto + iva

            venta = Ventas.objects.create(
                clientes=cliente,
                total_sin_iva=neto,
                total_iva=iva,
                total_con_iva=total,
                monto_pagado=total, # Asumir pago completo por ahora
                vuelto=0
            )

            for item in carrito:
                producto = get_object_or_404(Productos, codigo=item['codigo'])
                if item['cantidad'] > producto.stock_actual:
                    raise Exception(f"Stock insuficiente para {producto.nombre}")

                DetalleVenta.objects.create(
                    ventas=venta,
                    productos=producto,
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio']
                )
                producto.stock_actual -= item['cantidad']
                producto.save()

            return JsonResponse({'status': 'success', 'venta_id': venta.id})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    productos = Productos.objects.filter(stock_actual__gt=0)
    productos_json = serialize('json', productos, fields=('codigo', 'nombre', 'precio'))
    return render(request, 'ventas/form.html', {'productos_json': productos_json})


# =========================
# LISTAR VENTAS
# =========================
@login_required
def lista_ventas(request):
    ventas = Ventas.objects.all().order_by('-fecha')
    return render(request, 'ventas/lista_ventas.html', {'ventas': ventas})

# =========================
# Editar VENTAS
# =========================
@login_required
@user_passes_test(lambda u: es_vendedor(u) or es_admin(u))
@transaction.atomic
def editar_venta(request, venta_id):
    venta = get_object_or_404(Ventas, pk=venta_id)
    
    if request.method == 'POST':
        # La edición desde el POS implicaría una lógica más compleja
        # Por ahora, redirigimos a la lista
        return redirect('lista_ventas')

    productos = Productos.objects.filter(stock_actual__gt=0)
    productos_json = serialize('json', productos, fields=('codigo', 'nombre', 'precio'))
    
    detalles = DetalleVenta.objects.filter(ventas=venta)
    carrito = []
    for d in detalles:
        carrito.append({
            'codigo': d.productos.codigo,
            'nombre': d.productos.nombre,
            'precio': float(d.precio_unitario),
            'cantidad': d.cantidad
        })
    
    return render(request, 'ventas/form.html', {
        'productos_json': productos_json,
        'venta': venta,
        'carrito_json': json.dumps(carrito)
    })


# =========================
# Eliminar VENTAS
# =========================
@login_required
@user_passes_test(lambda u: es_vendedor(u) or es_admin(u))
@transaction.atomic
def eliminar_venta(request, venta_id):
    venta = get_object_or_404(Ventas, pk=venta_id)
    detalles = DetalleVenta.objects.filter(ventas=venta)

    if request.method == 'POST':
        # Devolver stock antes de eliminar
        for detalle in detalles:
            producto = detalle.productos
            producto.stock_actual += detalle.cantidad
            producto.save()

        venta.delete()
        return redirect('lista_ventas')

    return render(request, 'ventas/confirmar_eliminar.html', {'venta': venta})


# =========================
# VISTA PARA MOSTRAR COMPROBANTE EN HTML
# Solo usuarios autenticados
# =========================
@login_required
def comprobante_html(request, venta_id):
    venta = get_object_or_404(Ventas, pk=venta_id)
    detalles = DetalleVenta.objects.filter(ventas=venta)
    return render(request, 'ventas/comprobante.html', {
        'venta': venta,
        'detalles': detalles
    })


# =========================
# VISTA PARA GENERAR PDF DEL COMPROBANTE
# Solo usuarios autenticados
# =========================
from .models import Ventas, DetalleVenta

@login_required
def comprobante_pdf(request, venta_id):
    # Importar WeasyPrint solo aquí
    from weasyprint import HTML

    venta = get_object_or_404(Ventas, pk=venta_id)
    detalles = DetalleVenta.objects.filter(ventas=venta)

    html_string = render_to_string('ventas/comprobante.html', {
        'venta': venta,
        'detalles': detalles
    })

    html = HTML(string=html_string)
    result = tempfile.NamedTemporaryFile(delete=True)
    html.write_pdf(target=result.name)

    response = HttpResponse(result.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=comprobante_{venta_id}.pdf'
    return response