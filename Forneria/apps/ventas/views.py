from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from .models import Ventas, Clientes, DetalleVenta
from apps.inventario.models import Productos
from .forms import VentaForm, DetalleVentaForm

# Registrar venta con lógica de negocio
@transaction.atomic
def crear_venta(request):
    if request.method == 'POST':
        venta_form = VentaForm(request.POST)
        detalle_form = DetalleVentaForm(request.POST)

        if venta_form.is_valid() and detalle_form.is_valid():
            # Crear venta
            venta = venta_form.save(commit=False)

            # Obtener datos del detalle
            cantidad = detalle_form.cleaned_data['cantidad']
            producto = detalle_form.cleaned_data['productos']
            precio_unitario = detalle_form.cleaned_data['precio_unitario']
            descuento_pct = detalle_form.cleaned_data.get('descuento_pct', 0)

            # Validar stock
            if cantidad > producto.stock_actual:
                venta_form.add_error(None, f"Stock insuficiente para {producto.nombre}")
                return render(request, 'ventas/form.html', {'venta_form': venta_form, 'detalle_form': detalle_form})

            # Calcular totales
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

            # Crear detalle
            detalle = detalle_form.save(commit=False)
            detalle.ventas = venta
            detalle.save()

            # Actualizar stock
            producto.stock_actual -= cantidad
            producto.save()

            return redirect('lista_ventas')
    else:
        venta_form = VentaForm()
        detalle_form = DetalleVentaForm()

    return render(request, 'ventas/form.html', {'venta_form': venta_form, 'detalle_form': detalle_form})