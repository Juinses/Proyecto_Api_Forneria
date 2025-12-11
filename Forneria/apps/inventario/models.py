
# inventario/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Q, CheckConstraint
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
    identificador = models.CharField(max_length=50, unique=True, null=True)
    calorias = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    proteinas = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    grasas = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    carbohidratos = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    azucares = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    sodio = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.identificador

    class Meta:
        db_table = 'nutricional'


class Productos(models.Model):
    # NUEVO: código opcional y único para lookup rápido en ventas
    codigo = models.CharField(
        max_length=50, unique=True, blank=True, null=True,
        help_text="Código opcional único para ventas/lookup rápido."
    )

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
    nutricional = models.ForeignKey('Nutricional', on_delete=models.CASCADE, related_name='productos', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.marca})" if self.marca else self.nombre

    class Meta:
        db_table = 'producto'
        verbose_name_plural = "Productos"
        indexes = [
            models.Index(fields=['codigo']),       # nuevo índice
            models.Index(fields=['nombre']),
            models.Index(fields=['precio']),
            models.Index(fields=['caducidad']),
            models.Index(fields=['stock_actual']), # útil para reportes/alertas
        ]
        constraints = [
            CheckConstraint(check=Q(stock_actual__gte=0), name='ck_producto_stock_actual_no_negativo'),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.stock_minimo is not None and self.stock_maximo is not None:
            if self.stock_minimo > self.stock_maximo:
                raise ValidationError("El stock mínimo no puede ser mayor que el stock máximo.")
        if self.elaboracion and self.caducidad and self.caducidad < self.elaboracion:
            raise ValidationError("La fecha de caducidad no puede ser anterior a la fecha de elaboración.")

    # -------- Métodos utilitarios para ventas ----------
    @classmethod
    def find_by_id_or_code(cls, identifier_or_pk):
        """
        Recibe un string/código o un entero/pk y retorna el producto correspondiente.
        """
        try:
            pk = int(identifier_or_pk)
            return cls.objects.get(pk=pk)
        except (ValueError, cls.DoesNotExist):
            return cls.objects.get(codigo=identifier_or_pk)

    def puede_descontar(self, cantidad: int) -> bool:
        actual = self.stock_actual or 0
        return cantidad > 0 and actual - cantidad >= 0

    def descontar_stock(self, cantidad: int, registrar_movimiento: bool = True):
        if not self.puede_descontar(cantidad):
            raise ValueError(f"Stock insuficiente para {self} (solicitado: {cantidad}, actual: {self.stock_actual or 0})")
        self.stock_actual = (self.stock_actual or 0) - cantidad
        self.save(update_fields=['stock_actual', 'modificado'])
        if registrar_movimiento:
            MovimientosInventario.objects.create(
                tipo_movimiento=MovimientosInventario.SALIDA,
                cantidad=cantidad,
                productos=self
            )

    def reponer_stock(self, cantidad: int, registrar_movimiento: bool = True):
        if cantidad <= 0:
            raise ValueError("La cantidad a reponer debe ser > 0.")
        self.stock_actual = (self.stock_actual or 0) + cantidad
        self.save(update_fields=['stock_actual', 'modificado'])
        if registrar_movimiento:
            MovimientosInventario.objects.create(
                tipo_movimiento=MovimientosInventario.ENTRADA,
                cantidad=cantidad,
                productos=self
            )


class MovimientosInventario(models.Model):
    ENTRADA = 'ENTRADA'
    SALIDA = 'SALIDA'
    TIPOS = [
        (ENTRADA, 'Entrada'),
        (SALIDA, 'Salida'),
    ]

    tipo_movimiento = models.CharField(max_length=7, choices=TIPOS, db_index=True)  # index opcional
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
