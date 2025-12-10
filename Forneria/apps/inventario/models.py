
# inventario/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Categorias(models.Model):
    nombre = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.nombre if self.nombre else "Sin nombre"

    class Meta:
        db_table = 'categoria'
        verbose_name_plural = "Categorias"
        indexes = [
            models.Index(fields=['nombre']),
        ]


class Nutricional(models.Model):
    calorias = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    proteinas = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    grasas = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    carbohidratos = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    azucares = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    sodio = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"Nutr #{self.pk} (kcal={self.calorias})"

    class Meta:
        db_table = 'nutricional'


class Productos(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=300, blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    caducidad = models.DateField()
    elaboracion = models.DateField(blank=True, null=True)
    tipo = models.CharField(max_length=100, blank=True, null=True)
    stock_actual = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    stock_minimo = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    stock_maximo = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    presentacion = models.CharField(max_length=100, blank=True, null=True)
    formato = models.CharField(max_length=100, blank=True, null=True)

    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)
    eliminado = models.DateTimeField(blank=True, null=True)

    categorias = models.ForeignKey('Categorias', on_delete=models.PROTECT, related_name='productos')
    # 1:1 según diagrama entre Producto y Nutricional
    nutricional = models.OneToOneField('Nutricional', on_delete=models.CASCADE, related_name='producto')

    def __str__(self):
        return f"{self.nombre} ({self.marca})" if self.marca else self.nombre

    class Meta:
        db_table = 'producto'
        verbose_name_plural = "Productos"
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['precio']),
            models.Index(fields=['caducidad']),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.stock_minimo is not None and self.stock_maximo is not None:
            if self.stock_minimo > self.stock_maximo:
                raise ValidationError("El stock mínimo no puede ser mayor que el stock máximo.")
        if self.elaboracion and self.caducidad and self.caducidad < self.elaboracion:
            raise ValidationError("La fecha de caducidad no puede ser anterior a la fecha de elaboración.")


class MovimientosInventario(models.Model):
    ENTRADA = 'ENTRADA'
    SALIDA = 'SALIDA'
    TIPOS = [
        (ENTRADA, 'Entrada'),
        (SALIDA, 'Salida'),
    ]

    tipo_movimiento = models.CharField(max_length=7, choices=TIPOS)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    fecha = models.DateTimeField(auto_now_add=True)

    productos = models.ForeignKey('Productos', on_delete=models.CASCADE, related_name='movimientos')

    def __str__(self):
        return f"{self.tipo_movimiento} x{self.cantidad} - {self.productos.nombre}"

    class Meta:
        db_table = 'movimientos_inventario'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['productos']),
            models.Index(fields=['fecha']),
        ]
