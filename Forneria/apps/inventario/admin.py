
# inventario/admin.py
from django.contrib import admin
from django.db.models import F
from django.utils import timezone
from .models import Productos, Categorias, MovimientosInventario

@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'marca', 'precio', 'caducidad', 'stock_actual', 'stock_minimo', 'stock_maximo', 'categorias')
    search_fields = ('nombre', 'marca')
    list_filter = ('categorias', 'caducidad')
    date_hierarchy = 'caducidad'
    ordering = ('nombre',)
    list_editable = ('stock_actual',)  # edición rápida de stock
    list_select_related = ('categorias',)
    autocomplete_fields = ('categorias',)

    actions = ['entrada_stock_5', 'salida_stock_5']

    def entrada_stock_5(self, request, queryset):
        """
        Incrementa 5 unidades de stock en los productos seleccionados y registra movimiento.
        """
        count = 0
        for producto in queryset:
            producto.stock_actual = (producto.stock_actual or 0) + 5
            producto.save(update_fields=['stock_actual'])
            MovimientosInventario.objects.create(
                productos=producto,
                tipo_movimiento=MovimientosInventario.ENTRADA,
                cantidad=5,
                fecha=timezone.now()
            )
            count += 1
        self.message_user(request, f"Se aumentó stock (+5) en {count} productos.")
    entrada_stock_5.short_description = "Entrada de stock (+5) a seleccionados"

    def salida_stock_5(self, request, queryset):
        """
        Decrementa 5 unidades de stock (sin negativos) y registra movimiento.
        """
        count = 0
        for producto in queryset:
            actual = producto.stock_actual or 0
            if actual <= 0:
                continue
            qty = 5 if actual >= 5 else actual
            producto.stock_actual = actual - qty
            producto.save(update_fields=['stock_actual'])
            MovimientosInventario.objects.create(
                productos=producto,
                tipo_movimiento=MovimientosInventario.SALIDA,
                cantidad=qty,
                fecha=timezone.now()
            )
            count += 1
        self.message_user(request, f"Se redujo stock (-5) en {count} productos (evitando negativos).")
    salida_stock_5.short_description = "Salida de stock (-5) a seleccionados"


@admin.register(Categorias)
class CategoriasAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(MovimientosInventario)
class MovimientosInventarioAdmin(admin.ModelAdmin):
    list_display = ('productos', 'tipo_movimiento', 'cantidad', 'fecha')
    list_filter = ('tipo_movimiento', 'fecha')
    date_hierarchy = 'fecha'
    list_select_related = ('productos',)
    search_fields = ('productos__nombre',)
