from django import forms
from .models import Ventas, Clientes, DetalleVenta

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = ['rut', 'nombre', 'correo']

class VentaForm(forms.ModelForm):
    class Meta:
        model = Ventas
        fields = [
            'fecha', 'total_sin_iva', 'total_iva', 'descuento',
            'total_con_iva', 'canal_venta', 'folio', 'monto_pagado',
            'vuelto', 'clientes'
        ]

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['cantidad', 'precio_unitario', 'descuento_pct', 'ventas', 'productos']