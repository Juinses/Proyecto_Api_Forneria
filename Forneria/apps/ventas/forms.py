
from django import forms
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Ventas, Clientes, DetalleVenta
from apps.inventario.models import Productos

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = ['rut', 'nombre', 'correo']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class VentaForm(forms.ModelForm):
    class Meta:
        model = Ventas
        # Quita 'fecha' si es auto_now_add en el modelo
        fields = ['canal_venta', 'folio', 'monto_pagado', 'vuelto', 'clientes']
        widgets = {
            'canal_venta': forms.TextInput(attrs={'class': 'form-control'}),
            # Si canal_venta es choices en el modelo: usa Select
            'folio': forms.TextInput(attrs={'class': 'form-control'}),
            'monto_pagado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'vuelto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'clientes': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned = super().clean()
        monto = cleaned.get('monto_pagado')
        vuelto = cleaned.get('vuelto')
        if monto is not None and monto < 0:
            self.add_error('monto_pagado', 'El monto pagado no puede ser negativo.')
        if vuelto is not None and vuelto < 0:
            self.add_error('vuelto', 'El vuelto no puede ser negativo.')
        return cleaned


class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['cantidad', 'precio_unitario', 'descuento_pct', 'productos']
        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'descuento_pct': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'productos': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned = super().clean()
        cantidad = cleaned.get('cantidad')
        precio = cleaned.get('precio_unitario')
        descuento = cleaned.get('descuento_pct') or Decimal('0')

        if cantidad is None or cantidad < 1:
            self.add_error('cantidad', 'La cantidad debe ser al menos 1.')
        if precio is None or precio < 0:
            self.add_error('precio_unitario', 'El precio unitario no puede ser negativo.')
        if descuento < 0 or descuento > 100:
            self.add_error('descuento_pct', 'El descuento debe estar entre 0 y 100.')
        return cleaned
