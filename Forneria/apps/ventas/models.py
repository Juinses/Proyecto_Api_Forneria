from django.db import models


class Clientes(models.Model):
    rut = models.CharField(max_length=12, blank=True, null=True)
    nombre = models.CharField(max_length=150)
    correo = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'cliente'   # Django usará este nombre de tabla
        verbose_name_plural = "Clientes"


class Ventas(models.Model):
    fecha = models.DateTimeField()
    total_sin_iva = models.DecimalField(max_digits=10, decimal_places=2)
    total_iva = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2)
    total_con_iva = models.DecimalField(max_digits=10, decimal_places=2)
    canal_venta = models.CharField(max_length=10)
    folio = models.CharField(max_length=20, blank=True, null=True)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vuelto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    clientes = models.ForeignKey(Clientes, on_delete=models.CASCADE)

    class Meta:
        db_table = 'venta'
        verbose_name_plural = "Ventas"


class DetalleVenta(models.Model):
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_pct = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    ventas = models.ForeignKey(Ventas, on_delete=models.CASCADE)
    productos = models.ForeignKey('inventario.Productos', on_delete=models.CASCADE)

    class Meta:
        db_table = 'detalle_venta'
        verbose_name_plural = "Detalle_ventas"
