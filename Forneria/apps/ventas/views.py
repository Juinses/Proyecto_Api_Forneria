from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.contrib.auth.decorators import login_required, user_passes_test

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
        venta_form = VentaForm(request.POST)
        detalle_form = DetalleVentaForm(request.POST)

        if venta_form.is_valid() and detalle_form.is_valid():
            venta = venta_form.save(commit=False)

            cantidad = detalle_form.cleaned_data['cantidad']
            producto = detalle_form.cleaned_data['productos']
            precio_unitario = detalle_form.cleaned_data['precio_unitario']
            descuento_pct = detalle_form.cleaned_data.get('descuento_pct', 0)

            if cantidad > producto.stock_actual:
                venta_form.add_error(None, f"Stock insuficiente para {producto.nombre}")
                return render(request, 'ventas/form.html', {
                    'venta_form': venta_form,
                    'detalle_form': detalle_form
                })

            subtotal = cantidad * precio_unitario
            total_sin_iva = subtotal
            total_iva = round(total_sin_iva * 0.19, 2)
            descuento = round((subtotal * descuento_pct) / 100, 2)
            total_con_iva = total_sin_iva + total_iva - descuento

            venta.total_sin_iva = total_sin_iva
            venta.total_iva = total_iva
            venta.descuento = descuento
            venta.total_con_iva = total_con_iva
            venta.save()

            detalle = detalle_form.save(commit=False)
            detalle.ventas = venta
            detalle.save()

            producto.stock_actual -= cantidad
            producto.save()

            return redirect('lista_ventas')
    else:
        venta_form = VentaForm()
        detalle_form = DetalleVentaForm()

    return render(request, 'ventas/form.html', {
        'venta_form': venta_form,
        'detalle_form': detalle_form
    })


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
@login_required
def comprobante_pdf(request, venta_id):
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