
# ventas/admin.py
from django.contrib import admin
from django.utils.html import format_html
from decimal import Decimal
from .models import Ventas, Clientes, DetalleVenta

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    fields = ('productos', 'cantidad', 'precio_unitario', 'descuento_pct', 'subtotal_preview')
    readonly_fields = ('subtotal_preview',)
    autocomplete_fields = ('productos',)

    def subtotal_preview(self, obj):
        if not obj.pk:
            return '-'
        return f"{obj.subtotal():.2f}"
    subtotal_preview.short_description = 'Subtotal'

@admin.register(Ventas)
class VentasAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'clientes', 'total_con_iva', 'canal_venta', 'folio', 'comprobante_link')
    search_fields = ('folio', 'clientes__nombre')
    list_filter = ('fecha', 'canal_venta')
    date_hierarchy = 'fecha'
    ordering = ('-fecha',)
    list_select_related = ('clientes',)
    inlines = [DetalleVentaInline]
    readonly_fields = ('total_sin_iva', 'total_iva', 'total_con_iva')
    autocomplete_fields = ('clientes',)

    def save_model(self, request, obj, form, change):
        """
        Guarda la venta y recalcula totales para mantener consistencia.
        """
        super().save_model(request, obj, form, change)
        # Ajusta el IVA por defecto aquí si lo quieres diferente:
        obj.recalcular_totales(iva_pct=Decimal('0.19'))

    def comprobante_link(self, obj):
        # Asumiendo que tienes la vista 'comprobante_pdf' con nombre de url
        return format_html('/ventas/comprobante/{}/pdf/PDF</a>', obj.pk)
    comprobante_link.short_description = 'Comprobante'

@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre', 'correo')
    search_fields = ('nombre', 'rut')
    ordering = ('nombre',)

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('ventas', 'productos', 'cantidad', 'precio_unitario', 'descuento_pct', 'subtotal_col')
    search_fields = ('ventas__folio', 'productos__nombre')
    list_filter = ('ventas__fecha',)
    list_select_related = ('ventas', 'productos')

    def subtotal_col(self, obj):
        return f"{obj.subtotal():.2f}"
    subtotal_col.short_description = 'Subtotal'
