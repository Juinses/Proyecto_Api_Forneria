
from django import forms
from .models import Productos, Categorias, MovimientosInventario, Nutricional
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class ProductoForm(forms.ModelForm):
    # Opcional: si prefieres controlar explícitamente el widget de nutricional
    nutricional = forms.ModelChoiceField(
        queryset=Nutricional.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Productos
        fields = [
            'nombre', 'descripcion', 'marca', 'precio', 'caducidad',
            'elaboracion', 'tipo', 'stock_actual', 'stock_minimo',
            'stock_maximo', 'presentacion', 'formato',
            'categorias', 'nutricional'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'caducidad': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'elaboracion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            # Si NO tienes choices en el modelo, usa TextInput:
            'tipo': forms.TextInput(attrs={'class': 'form-control'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'stock_maximo': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'presentacion': forms.TextInput(attrs={'class': 'form-control'}),
            # Si NO tienes choices en el modelo, usa TextInput:
            'formato': forms.TextInput(attrs={'class': 'form-control'}),
            # ForeignKey → Select (NO múltiples)
            'categorias': forms.Select(attrs={'class': 'form-select'}),
            # OneToOne/ForeignKey → Select (NO textarea)
            # 'nutricional': forms.Select(attrs={'class': 'form-select'}),  # si no usas ModelChoiceField arriba
        }

    def clean(self):
        cleaned = super().clean()
        stock_min = cleaned.get('stock_minimo')
        stock_max = cleaned.get('stock_maximo')
        elaboracion = cleaned.get('elaboracion')
        caducidad = cleaned.get('caducidad')

        if stock_min is not None and stock_max is not None and stock_min > stock_max:
            self.add_error('stock_minimo', 'El stock mínimo no puede ser mayor que el stock máximo.')
            self.add_error('stock_maximo', 'El stock máximo debe ser mayor o igual que el stock mínimo.')

        if elaboracion and caducidad and caducidad < elaboracion:
            self.add_error('caducidad', 'La fecha de caducidad no puede ser anterior a la fecha de elaboración.')

        return cleaned


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categorias
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class MovimientoInventarioForm(forms.ModelForm):
    class Meta:
        model = MovimientosInventario
        fields = ['tipo_movimiento', 'cantidad', 'productos']
        widgets = {
            'tipo_movimiento': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'productos': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is None or cantidad < 1:
            raise forms.ValidationError('La cantidad debe ser un entero positivo.')
        return cantidad
