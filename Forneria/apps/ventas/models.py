# ventas/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Clientes(models.Model):
    rut = models.CharField(max_length=12, blank=True, null=True)
    nombre = models.CharField(max_length=150)
    correo = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.rut})" if self.rut else self.nombre

    class Meta:
        db_table = 'cliente'
        verbose_name_plural = "Clientes"
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['rut']),
        ]


class Ventas(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    total_sin_iva = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_iva = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_con_iva = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    canal_venta = models.CharField(max_length=10)
    folio = models.CharField(max_length=20, blank=True, null=True)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vuelto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    clientes = models.ForeignKey(Clientes, on_delete=models.PROTECT, related_name='ventas')

    def __str__(self):
        return f"Venta #{self.id} - {self.clientes.nombre}"

    class Meta:
        db_table = 'venta'
        ordering = ['-fecha']

    # ---------------------------
    #  RECALCULAR TOTALES
    # ---------------------------
    def recalcular_totales(self, iva_pct=Decimal('0.19')):
        subtotales = [d.subtotal() for d in self.detalles.all()]
        total_sin_iva = sum(subtotales, Decimal('0.00'))

        # aplicar descuento
        total_sin_iva_desc = total_sin_iva - (self.descuento or Decimal('0.00'))
        if total_sin_iva_desc < 0:
            total_sin_iva_desc = Decimal('0.00')

        total_iva = (total_sin_iva_desc * iva_pct).quantize(Decimal('0.01'))
        total_con_iva = (total_sin_iva_desc + total_iva).quantize(Decimal('0.01'))

        self.total_sin_iva = total_sin_iva
        self.total_iva = total_iva
        self.total_con_iva = total_con_iva

        # volver a calcular vuelto si corresponde
        if self.monto_pagado is not None:
            self.vuelto = max(self.monto_pagado - total_con_iva, Decimal('0.00'))

        self.save(update_fields=['total_sin_iva', 'total_iva', 'total_con_iva', 'vuelto'])


class DetalleVenta(models.Model):
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_pct = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    ventas = models.ForeignKey(Ventas, on_delete=models.CASCADE, related_name='detalles')
    productos = models.ForeignKey('inventario.Productos', on_delete=models.PROTECT, related_name='detalles_venta')

    def __str__(self):
        return f"{self.productos.nombre} x{self.cantidad}"

    class Meta:
        db_table = 'detalle_venta'
        indexes = [
            models.Index(fields=['ventas']),
            models.Index(fields=['productos']),
        ]

    # ---------------------------
    # SUBTOTAL
    # ---------------------------
    def subtotal(self):
        bruto = self.cantidad * self.precio_unitario
        desc_pct = (self.descuento_pct or Decimal('0'))
        factor = (Decimal('100') - desc_pct) / Decimal('100')
        return (bruto * factor).quantize(Decimal('0.01'))

    # ---------------------------
    # SAVE: Recalcular + Descontar stock
    # ---------------------------
    def save(self, *args, **kwargs):
        is_new = self.pk is None

        super().save(*args, **kwargs)

        # DESCONTAR STOCK SOLO LA PRIMERA VEZ
        if is_new:
            producto = self.productos
            producto.stock_actual -= self.cantidad
            if producto.stock_actual < 0:
                raise ValueError("Stock insuficiente para realizar esta venta.")
            producto.save(update_fields=['stock_actual'])

        # Recalcular totales de venta
        self.ventas.recalcular_totales()
