# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Alertas(models.Model):
    tipo_alerta = models.CharField(max_length=8)
    mensaje = models.CharField(max_length=255)
    fecha_generada = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)
    productos = models.ForeignKey('Productos', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'alertas'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150, db_collation='utf8mb3_spanish_ci')

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group_id = models.IntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group_id', 'permission_id'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255, db_collation='utf8mb3_spanish_ci')
    content_type_id = models.IntegerField()
    codename = models.CharField(max_length=100, db_collation='utf8mb3_spanish_ci')

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type_id', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128, db_collation='utf8mb3_spanish_ci')
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150, db_collation='utf8mb3_spanish_ci')
    first_name = models.CharField(max_length=150, db_collation='utf8mb3_spanish_ci')
    last_name = models.CharField(max_length=150, db_collation='utf8mb3_spanish_ci')
    email = models.CharField(max_length=254, db_collation='utf8mb3_spanish_ci')
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.IntegerField()
    group_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user_id', 'group_id'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.IntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user_id', 'permission_id'),)


class Cargo(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=45, db_collation='utf8mb3_spanish_ci')
    descripcion = models.CharField(max_length=45, db_collation='utf8mb3_spanish_ci')

    class Meta:
        managed = False
        db_table = 'cargo'


class Categorias(models.Model):
    nombre = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categorias'


class Clientes(models.Model):
    rut = models.CharField(max_length=12, blank=True, null=True)
    nombre = models.CharField(max_length=150)
    correo = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clientes'


class Contrato(models.Model):
    pk = models.CompositePrimaryKey('id', 'empleado_id')
    id = models.IntegerField()
    detalle_contrato = models.CharField(max_length=45)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    empleado = models.ForeignKey('Empleado', models.DO_NOTHING)
    cargo = models.ForeignKey(Cargo, models.DO_NOTHING)
    departamento = models.ForeignKey('Departamento', models.DO_NOTHING)
    turno_has_jornada = models.ForeignKey('TurnoHasJornada', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'contrato'


class CuentaBancaria(models.Model):
    id = models.IntegerField(primary_key=True)
    banco = models.CharField(max_length=45, db_collation='utf8mb3_spanish_ci')
    tipo_cuenta = models.CharField(max_length=45, db_collation='utf8mb3_spanish_ci')
    numero_cuenta = models.IntegerField()
    correo = models.CharField(max_length=45, db_collation='utf8mb3_spanish_ci')
    empleado = models.ForeignKey('Empleado', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cuenta_bancaria'


class Departamento(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=45, db_collation='utf8mb3_spanish_ci')
    descripcion = models.CharField(max_length=45, db_collation='utf8mb3_spanish_ci')

    class Meta:
        managed = False
        db_table = 'departamento'


class DetalleVenta(models.Model):
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_pct = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    ventas = models.ForeignKey('Ventas', models.DO_NOTHING)
    productos = models.ForeignKey('Productos', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'detalle_venta'


class Direccion(models.Model):
    calle = models.CharField(max_length=100, db_collation='utf8mb3_general_ci')
    numero = models.CharField(max_length=10, db_collation='utf8mb3_general_ci')
    depto = models.CharField(max_length=10, db_collation='utf8mb3_general_ci', blank=True, null=True)
    comuna = models.CharField(max_length=100, db_collation='utf8mb3_general_ci')
    region = models.CharField(max_length=100, db_collation='utf8mb3_general_ci')
    codigo_postal = models.CharField(max_length=45, db_collation='utf8mb3_general_ci', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'direccion'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(db_collation='utf8mb3_spanish_ci', blank=True, null=True)
    object_repr = models.CharField(max_length=200, db_collation='utf8mb3_spanish_ci')
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField(db_collation='utf8mb3_spanish_ci')
    content_type_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100, db_collation='utf8mb3_spanish_ci')
    model = models.CharField(max_length=100, db_collation='utf8mb3_spanish_ci')

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255, db_collation='utf8mb3_spanish_ci')
    name = models.CharField(max_length=255, db_collation='utf8mb3_spanish_ci')
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40, db_collation='utf8mb3_spanish_ci')
    session_data = models.TextField(db_collation='utf8mb3_spanish_ci')
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Empleado(models.Model):
    nombres = models.CharField(max_length=100)
    a_paterno = models.CharField(db_column='A_paterno', max_length=45)  # Field name made lowercase.
    a_materno = models.CharField(db_column='A_materno', max_length=45)  # Field name made lowercase.
    run = models.CharField(unique=True, max_length=45)
    correo = models.CharField(max_length=100)
    fono = models.IntegerField(unique=True)
    clave = models.CharField(max_length=45)
    nacionalidad = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'empleado'


class FormaPago(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=45, db_collation='utf8mb3_spanish_ci')
    descripcion = models.CharField(max_length=45, db_collation='utf8mb3_spanish_ci')
    pago = models.ForeignKey('Pago', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'forma_pago'


class Jornada(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=45, db_collation='utf8mb3_spanish_ci')
    horas_semanales = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'jornada'


class Liquidacion(models.Model):
    id = models.IntegerField(primary_key=True)
    periodo = models.DateField()
    imponible = models.IntegerField()
    no_imponible = models.IntegerField()
    tributable = models.IntegerField()
    descuentos = models.IntegerField()
    bruto = models.IntegerField()
    liquido = models.IntegerField()
    fecha_cierre = models.DateField()
    estado = models.CharField(max_length=45)
    contrato = models.ForeignKey(Contrato, models.DO_NOTHING)
    contrato_empleado = models.ForeignKey(Contrato, models.DO_NOTHING, to_field='empleado_id', related_name='liquidacion_contrato_empleado_set')

    class Meta:
        managed = False
        db_table = 'liquidacion'


class MovimientosInventario(models.Model):
    tipo_movimiento = models.CharField(max_length=7)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField()
    productos = models.ForeignKey('Productos', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'movimientos_inventario'


class Nutricional(models.Model):
    calorias = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    proteinas = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    grasas = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    carbohidratos = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    azucares = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sodio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nutricional'


class Pago(models.Model):
    id = models.IntegerField(primary_key=True)
    fecha_pago = models.DateField()
    monto = models.IntegerField()
    comprobante = models.CharField(max_length=45, db_collation='utf8mb3_spanish_ci')
    estado = models.CharField(max_length=45, db_collation='utf8mb3_spanish_ci')
    liquidacion = models.ForeignKey(Liquidacion, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'pago'


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
    creado = models.DateTimeField(blank=True, null=True)
    modificado = models.DateTimeField(blank=True, null=True)
    eliminado = models.DateTimeField(blank=True, null=True)
    categorias = models.ForeignKey(Categorias, models.DO_NOTHING)
    nutricional = models.ForeignKey(Nutricional, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'productos'


class Roles(models.Model):
    nombre = models.CharField(max_length=100, db_collation='utf8mb3_general_ci')
    descripcion = models.CharField(max_length=200, db_collation='utf8mb3_general_ci', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'roles'


class Turno(models.Model):
    id = models.IntegerField(primary_key=True)
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()

    class Meta:
        managed = False
        db_table = 'turno'


class TurnoHasJornada(models.Model):
    turno = models.ForeignKey(Turno, models.DO_NOTHING)
    jornada = models.ForeignKey(Jornada, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'turno_has_jornada'


class Usuarios(models.Model):
    nombres = models.CharField(max_length=100, db_collation='utf8mb3_general_ci')
    paterno = models.CharField(max_length=100, db_collation='utf8mb3_general_ci')
    materno = models.CharField(max_length=100, db_collation='utf8mb3_general_ci', blank=True, null=True)
    run = models.CharField(unique=True, max_length=10, db_collation='utf8mb3_general_ci')
    correo = models.CharField(max_length=100, db_collation='utf8mb3_general_ci')
    fono = models.IntegerField(blank=True, null=True)
    clave = models.CharField(max_length=150, db_collation='utf8mb3_general_ci', blank=True, null=True)
    direccion = models.ForeignKey(Direccion, models.DO_NOTHING, db_column='Direccion_id')  # Field name made lowercase.
    roles = models.ForeignKey(Roles, models.DO_NOTHING, db_column='Roles_id')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuarios'


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
    clientes = models.ForeignKey(Clientes, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'ventas'
