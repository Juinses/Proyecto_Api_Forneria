from django.contrib import admin
from .models import Productos, Categorias, MovimientosInventario

@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'caducidad', 'stock_actual', 'categorias')
    search_fields = ('nombre', 'marca')
    list_filter = ('categorias', 'caducidad')

@admin.register(Categorias)
class CategoriasAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')

@admin.register(MovimientosInventario)
class MovimientosInventarioAdmin(admin.ModelAdmin):
    list_display = ('productos', 'tipo_movimiento', 'cantidad', 'fecha')
    list_filter = ('tipo_movimiento',)