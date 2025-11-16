from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile

from .models import Ventas, Clientes, DetalleVenta
from apps.inventario.models import Productos
from .forms import VentaForm, DetalleVentaForm


# =========================
# REGISTRAR VENTA CON LÓGICA DE NEGOCIO
# =========================
@transaction.atomic
def crear_venta(request):
    if request.method == 'POST':
        venta_form = VentaForm(request.POST)
        detalle_form = DetalleVentaForm(request.POST)

        if venta_form.is_valid() and detalle_form.is_valid():
            # Crear venta sin guardar aún (para calcular totales)
            venta = venta_form.save(commit=False)

            # Obtener datos del detalle
            cantidad = detalle_form.cleaned_data['cantidad']
            producto = detalle_form.cleaned_data['productos']
            precio_unitario = detalle_form.cleaned_data['precio_unitario']
            descuento_pct = detalle_form.cleaned_data.get('descuento_pct', 0)

            # Validar stock disponible
            if cantidad > producto.stock_actual:
                venta_form.add_error(None, f"Stock insuficiente para {producto.nombre}")
                return render(request, 'ventas/form.html', {
                    'venta_form': venta_form,
                    'detalle_form': detalle_form
                })

            # Calcular totales
            subtotal = cantidad * precio_unitario
            total_sin_iva = subtotal
            total_iva = round(total_sin_iva * 0.19, 2)  # IVA 19%
            descuento = round((subtotal * descuento_pct) / 100, 2)
            total_con_iva = total_sin_iva + total_iva - descuento

            # Asignar valores calculados a la venta
            venta.total_sin_iva = total_sin_iva
            venta.total_iva = total_iva
            venta.descuento = descuento
            venta.total_con_iva = total_con_iva
            venta.save()

            # Crear detalle de venta
            detalle = detalle_form.save(commit=False)
            detalle.ventas = venta
            detalle.save()

            # Actualizar stock del producto
            producto.stock_actual -= cantidad
            producto.save()

            # Redirigir a la lista de ventas
            return redirect('lista_ventas')
    else:
        # Si es GET, mostrar formulario vacío
        venta_form = VentaForm()
        detalle_form = DetalleVentaForm()

    # Renderizar formulario (GET o POST inválido)
    return render(request, 'ventas/form.html', {
        'venta_form': venta_form,
        'detalle_form': detalle_form
    })


# =========================
# VISTA PARA MOSTRAR COMPROBANTE EN HTML
# =========================
def comprobante_html(request, venta_id):
    # Obtener venta y sus detalles
    venta = get_object_or_404(Ventas, pk=venta_id)
    detalles = DetalleVenta.objects.filter(ventas=venta)

    # Renderizar plantilla HTML
    return render(request, 'ventas/comprobante.html', {
        'venta': venta,
        'detalles': detalles
    })


# =========================
# VISTA PARA GENERAR PDF DEL COMPROBANTE
# =========================
def comprobante_pdf(request, venta_id):
    # Obtener venta y detalles
    venta = get_object_or_404(Ventas, pk=venta_id)
    detalles = DetalleVenta.objects.filter(ventas=venta)

    # Renderizar HTML como string
    html_string = render_to_string('ventas/comprobante.html', {
        'venta': venta,
        'detalles': detalles
    })

    # Convertir HTML a PDF usando WeasyPrint
    html = HTML(string=html_string)
    result = tempfile.NamedTemporaryFile(delete=True)
    html.write_pdf(target=result.name)

    # Responder con el PDF
    response = HttpResponse(result.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=comprobante_{venta_id}.pdf'
    return response