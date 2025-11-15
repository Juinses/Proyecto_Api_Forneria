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

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categorias
        fields = ['nombre', 'descripcion']

class MovimientoInventarioForm(forms.ModelForm):
    class Meta:
        model = MovimientosInventario
        fields = ['tipo_movimiento', 'cantidad', 'productos']
