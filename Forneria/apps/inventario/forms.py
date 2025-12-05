from django import forms
from .models import Productos, Categorias, MovimientosInventario

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = [
            'nombre', 'descripcion', 'marca', 'precio', 'caducidad',
            'elaboracion', 'tipo', 'stock_actual', 'stock_minimo',
            'stock_maximo', 'presentacion', 'formato', 'categorias', 'nutricional'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'caducidad': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'elaboracion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_maximo': forms.NumberInput(attrs={'class': 'form-control'}),
            'presentacion': forms.TextInput(attrs={'class': 'form-control'}),
            'formato': forms.Select(attrs={'class': 'form-select'}),
            'categorias': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'nutricional': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categorias
        fields = ['nombre', 'descripcion']

class MovimientoInventarioForm(forms.ModelForm):
    class Meta:
        model = MovimientosInventario
        fields = ['tipo_movimiento', 'cantidad', 'productos']
