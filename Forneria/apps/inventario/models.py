from django.db import models


class Categorias(models.Model):
    nombre = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.nombre if self.nombre else "Sin nombre"
    class Meta:
        db_table = 'categoria'   # nombre de la tabla en la BD
        verbose_name_plural = "Categorias"

class Nutricional(models.Model):
    calorias = models.IntegerField(blank=True, null=True)
    proteinas = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    grasas = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    carbohidratos = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    azucares = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    sodio = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'nutricional'

class Productos(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=300, blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    caducidad = models.DateField()
    elaboracion = models.DateField(blank=True, null=True)
    tipo = models.CharField(max_length=100, blank=True, null=True)
    stock_actual = models.IntegerField(blank=True, null=True)
    stock_minimo = models.IntegerField(blank=True, null=True)
    stock_maximo = models.IntegerField(blank=True, null=True)
    presentacion = models.CharField(max_length=100, blank=True, null=True)
    formato = models.CharField(max_length=100, blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)
    eliminado = models.DateTimeField(blank=True, null=True)
    categorias = models.ForeignKey(Categorias, on_delete=models.CASCADE)
    nutricional = models.ForeignKey(Nutricional, on_delete=models.CASCADE)
    class Meta:
        db_table = 'producto'
        verbose_name_plural = "Productos"


class MovimientosInventario(models.Model):
    tipo_movimiento = models.CharField(max_length=7)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField()
    productos = models.ForeignKey(Productos, on_delete=models.CASCADE)

    class Meta:
        db_table = 'movimientos_inventario'
