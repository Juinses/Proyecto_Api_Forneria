from django.contrib import admin
from .models import Ventas, Clientes, DetalleVenta

@admin.register(Ventas)
class VentasAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'clientes', 'total_con_iva', 'canal_venta', 'folio')
    search_fields = ('folio', 'clientes__nombre')
    list_filter = ('fecha', 'canal_venta')

@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre', 'correo')
    search_fields = ('nombre', 'rut')

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('ventas', 'productos', 'cantidad', 'precio_unitario', 'descuento_pct')