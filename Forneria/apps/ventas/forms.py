from django import forms
from .models import Ventas, Clientes, DetalleVenta
from apps.inventario.models import Productos

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = ['rut', 'nombre', 'correo']

class VentaForm(forms.ModelForm):
    class Meta:
        model = Ventas
        fields = [
            'fecha', 'canal_venta', 'folio', 'monto_pagado',
            'vuelto', 'clientes'
        ]

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['cantidad', 'precio_unitario', 'descuento_pct', 'productos']