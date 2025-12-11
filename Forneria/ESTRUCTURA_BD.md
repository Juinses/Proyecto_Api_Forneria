# 🗄️ Estructura de Base de Datos

## Diagrama de Relaciones

```
┌─────────────────┐
│    Usuarios     │
│  (Django Auth)  │
├─────────────────┤
│ id (PK)         │
│ username        │
│ password        │
│ is_superuser    │
│ groups (M2M)    │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
    ┌──────────┐    ┌──────────────┐
    │ Vendedor │    │ Admin (Super)│
    └──────────┘    └──────────────┘

┌──────────────────┐
│    Categorias    │
├──────────────────┤
│ id (PK)          │
│ nombre           │
│ descripcion      │
└────────┬─────────┘
         │
         │ (1:M)
         ▼
┌──────────────────────┐       ┌──────────────┐
│     Productos        │──────▶│ Nutricional  │
├──────────────────────┤       ├──────────────┤
│ id (PK)              │       │ id (PK)      │
│ codigo (UNIQUE)      │       │ identificador│
│ nombre               │       │ calorias     │
│ descripcion          │       │ proteinas    │
│ marca                │       │ grasas       │
│ precio               │       │ carbohidratos│
│ caducidad            │       │ azucares     │
│ elaboracion          │       │ sodio        │
│ stock_actual         │       └──────────────┘
│ stock_minimo         │
│ stock_maximo         │ 1:M    ┌────────────────┐
│ presentacion         │───────▶│ DetalleVenta   │
│ formato              │        ├────────────────┤
│ categorias_id (FK)   │        │ id (PK)        │
│ nutricional_id (FK)  │        │ cantidad       │
│ creado               │        │ precio_unit    │
│ modificado           │        │ descuento_pct  │
│ eliminado (soft del) │        │ ventas_id (FK) │
└──────────────────────┘        │ productos_id (FK)
                                └────────────────┘
                                     ▲
                                     │
┌──────────────────┐                 │
│     Clientes     │                 │
├──────────────────┤                 │
│ id (PK)          │                 │
│ rut              │                 │
│ nombre           │              M:1│
│ correo           │                 │
└────────┬─────────┘                 │
         │                           │
         │ M:1                       │
         │                           │
         ▼                           │
    ┌──────────────┐      ┌──────────────────┐
    │    Ventas    │─────▶│  DetalleVenta    │
    ├──────────────┤  M:1 └──────────────────┘
    │ id (PK)      │
    │ fecha        │
    │ total_s_iva  │
    │ total_iva    │
    │ total_c_iva  │
    │ descuento    │
    │ canal_venta  │
    │ folio        │
    │ monto_pagado │
    │ vuelto       │
    │ clientes_id  │
    └──────────────┘

┌────────────────────────────┐
│ MovimientosInventario      │
├────────────────────────────┤
│ id (PK)                    │
│ tipo (entrada/salida)      │
│ cantidad                   │
│ razon                      │
│ productos_id (FK)          │
│ fecha                      │
└────────────────────────────┘
```

---

## 📊 Tablas Detalladas

### 🔐 **auth_user** (Django)
| Campo | Tipo | Notas |
|-------|------|-------|
| id | AutoField | PK |
| username | CharField(150) | Único |
| password | CharField(128) | Hash bcrypt |
| first_name | CharField(150) | Opcional |
| last_name | CharField(150) | Opcional |
| email | EmailField | Opcional |
| is_staff | Boolean | Admin site |
| is_active | Boolean | Usuario activo |
| is_superuser | Boolean | Permisos totales |
| last_login | DateTime | Última sesión |
| date_joined | DateTime | Fecha creación |

### 👥 **auth_group** (Django)
| Campo | Tipo | Notas |
|-------|------|-------|
| id | AutoField | PK |
| name | CharField(150) | Único ("Vendedor", "Admin") |

### 🛒 **categoria**
```sql
CREATE TABLE categoria (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100),
    descripcion VARCHAR(200),
    INDEX idx_nombre (nombre)
);
```

### 🥖 **producto**
```sql
CREATE TABLE producto (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    codigo VARCHAR(50) UNIQUE NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(300),
    marca VARCHAR(100),
    precio DECIMAL(10,2) NOT NULL,
    caducidad DATE NOT NULL,
    elaboracion DATE NULL,
    tipo VARCHAR(100),
    stock_actual INTEGER NULL CONSTRAINT ck_stock_no_neg CHECK (stock_actual >= 0),
    stock_minimo INTEGER NULL,
    stock_maximo INTEGER NULL,
    presentacion VARCHAR(100),
    formato VARCHAR(100),
    creado DATETIME DEFAULT CURRENT_TIMESTAMP,
    modificado DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    eliminado DATETIME NULL,
    categoria_id INTEGER NOT NULL FOREIGN KEY REFERENCES categoria(id),
    nutricional_id INTEGER NULL FOREIGN KEY REFERENCES nutricional(id),
    
    INDEX idx_codigo (codigo),
    INDEX idx_nombre (nombre),
    INDEX idx_precio (precio),
    INDEX idx_caducidad (caducidad),
    INDEX idx_stock_actual (stock_actual)
);
```

**Notas importantes:**
- `eliminado IS NULL` = producto activo
- `eliminado IS NOT NULL` = producto eliminado (soft delete)
- `stock_actual` puede ser 0 (producto sin stock pero visible)
- `codigo` es único pero opcional (fallback a `id`)
- `nutricional_id` es ahora NULLABLE (relación ForeignKey, no OneToOne)
- Múltiples productos pueden compartir la misma información nutricional

### 👨‍🍳 **nutricional**
```sql
CREATE TABLE nutricional (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    identificador VARCHAR(50) UNIQUE NULL,
    calorias INTEGER NULL CONSTRAINT ck_cal_non_neg CHECK (calorias >= 0),
    proteinas DECIMAL(6,2) NULL CONSTRAINT ck_prot_non_neg CHECK (proteinas >= 0),
    grasas DECIMAL(6,2) NULL CONSTRAINT ck_gras_non_neg CHECK (grasas >= 0),
    carbohidratos DECIMAL(6,2) NULL CONSTRAINT ck_carb_non_neg CHECK (carbohidratos >= 0),
    azucares DECIMAL(6,2) NULL CONSTRAINT ck_azuc_non_neg CHECK (azucares >= 0),
    sodio DECIMAL(6,2) NULL CONSTRAINT ck_sod_non_neg CHECK (sodio >= 0)
);
```

**Cambio reciente:** Ahora es relación de **uno-a-muchos** (ForeignKey) en lugar de uno-a-uno (OneToOneField). Esto permite que múltiples productos reutilicen la misma información nutricional.

### 🧑‍💼 **cliente**
```sql
CREATE TABLE cliente (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    rut VARCHAR(12) NULL,
    nombre VARCHAR(150) NOT NULL,
    correo VARCHAR(100) NULL,
    
    INDEX idx_nombre (nombre),
    INDEX idx_rut (rut)
);
```

**Nota:** Cliente con `id=1` y `nombre='Varios'` es por defecto para ventas sin cliente específico.

### 💵 **venta**
```sql
CREATE TABLE venta (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_sin_iva DECIMAL(10,2) DEFAULT 0.00,
    total_iva DECIMAL(10,2) DEFAULT 0.00,
    descuento DECIMAL(10,2) DEFAULT 0.00,
    total_con_iva DECIMAL(10,2) DEFAULT 0.00,
    canal_venta VARCHAR(10),  -- 'TIENDA', 'DELIVERY', etc.
    folio VARCHAR(20) NULL,
    monto_pagado DECIMAL(10,2) NULL,
    vuelto DECIMAL(10,2) NULL,
    cliente_id INTEGER NOT NULL FOREIGN KEY REFERENCES cliente(id),
    
    INDEX idx_fecha (fecha),
    INDEX idx_cliente (cliente_id),
    ORDERING: ORDER BY fecha DESC
);
```

### 📝 **detalle_venta**
```sql
CREATE TABLE detalle_venta (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    cantidad INTEGER NOT NULL CONSTRAINT ck_cant_min CHECK (cantidad >= 1),
    precio_unitario DECIMAL(10,2) NOT NULL,
    descuento_pct DECIMAL(5,2) NULL CONSTRAINT ck_desc_range CHECK (descuento_pct BETWEEN 0 AND 100),
    venta_id INTEGER NOT NULL FOREIGN KEY REFERENCES venta(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL FOREIGN KEY REFERENCES producto(id) ON DELETE PROTECT,
    
    INDEX idx_venta (venta_id),
    INDEX idx_producto (producto_id)
);
```

### 📦 **movimiento_inventario**
```sql
CREATE TABLE movimientosinventario (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    tipo VARCHAR(20),  -- 'entrada', 'salida'
    cantidad INTEGER NOT NULL,
    razon VARCHAR(200),
    producto_id INTEGER NOT NULL FOREIGN KEY REFERENCES producto(id),
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_producto (producto_id),
    INDEX idx_fecha (fecha)
);
```

---

## 🔍 Queries Útiles

### Productos activos:
```sql
SELECT * FROM producto WHERE eliminado IS NULL;
```

### Productos sin stock:
```sql
SELECT * FROM producto 
WHERE eliminado IS NULL 
AND stock_actual = 0;
```

### Total de ventas por cliente:
```sql
SELECT cliente_id, COUNT(*) as cantidad, SUM(total_con_iva) as total
FROM venta
GROUP BY cliente_id
ORDER BY total DESC;
```

### Productos próximos a vencer:
```sql
SELECT * FROM producto
WHERE eliminado IS NULL
AND caducidad BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 7 DAY)
ORDER BY caducidad ASC;
```

### Movimientos de un producto:
```sql
SELECT m.*, p.nombre
FROM movimientosinventario m
JOIN producto p ON m.producto_id = p.id
WHERE p.id = ?
ORDER BY m.fecha DESC;
```

### Historial de ventas:
```sql
SELECT v.*, c.nombre as cliente_nombre, COUNT(dv.id) as items
FROM venta v
JOIN cliente c ON v.cliente_id = c.id
LEFT JOIN detalle_venta dv ON v.id = dv.venta_id
GROUP BY v.id
ORDER BY v.fecha DESC;
```

---

## 📋 Constraints e Índices

### Primary Keys:
- `producto.id`
- `categoria.id`
- `nutricional.id`
- `cliente.id`
- `venta.id`
- `detalle_venta.id`
- `movimientosinventario.id`

### Unique Keys:
- `producto.codigo` (NULL allowed)
- `nutricional.identificador` (NULL allowed)

### Foreign Keys:
- `producto.categoria_id` → `categoria.id` (PROTECT)
- `producto.nutricional_id` → `nutricional.id` (CASCADE)
- `venta.cliente_id` → `cliente.id` (PROTECT)
- `detalle_venta.venta_id` → `venta.id` (CASCADE)
- `detalle_venta.producto_id` → `producto.id` (PROTECT)
- `movimientosinventario.producto_id` → `producto.id` (PROTECT)

### Check Constraints:
- `producto.stock_actual >= 0`
- `nutricional.calorias >= 0`
- `detalle_venta.cantidad >= 1`
- `detalle_venta.descuento_pct BETWEEN 0 AND 100`

### Índices:
- `producto.codigo`
- `producto.nombre`
- `producto.precio`
- `producto.caducidad`
- `producto.stock_actual`
- `categoria.nombre`
- `cliente.nombre`
- `cliente.rut`
- `venta.fecha`
- `venta.cliente_id`
- `detalle_venta.venta_id`
- `detalle_venta.producto_id`

---

## 🔄 Relaciones y Cascadas

### Eliminar una categoría:
❌ **NO se puede** - PROTECT constraint
- Primero elimina todos los productos de esa categoría

### Eliminar un producto:
✅ **SÍ se puede** - Soft delete (marca eliminado = NOW())
- Los detalles de venta existentes permanecen
- El producto ya no aparece en búsquedas futuras

### Eliminar una venta:
✅ **SÍ se puede** - Cascade delete
- Se eliminan automáticamente todos los DetalleVenta
- Se devuelve stock (si se implementa lógica)

### Eliminar un cliente:
❌ **NO se puede** - PROTECT constraint
- Si tiene ventas asociadas

### Eliminar un detalle de venta:
⚠️ **Cuidado** - Afecta totales de la venta
- Implementa `venta.recalcular_totales()` después

---

## 📊 Migración de datos

### Crear backup:
```bash
# MySQL/MariaDB
mysqldump -u usuario -p forneria_db > backup.sql

# PostgreSQL
pg_dump -U usuario forneria_db > backup.sql
```

### Restaurar backup:
```bash
# MySQL/MariaDB
mysql -u usuario -p forneria_db < backup.sql

# PostgreSQL
psql -U usuario forneria_db < backup.sql
```

### Exportar/Importar con Django:
```bash
# Exportar a JSON
python manage.py dumpdata > datos.json

# Importar desde JSON
python manage.py loaddata datos.json
```

---

**Esta estructura permite:**
- ✅ Ventas sin reducción automática de stock
- ✅ Productos con stock 0 visibles en ventas
- ✅ Historial completo de movimientos
- ✅ Información nutricional opcional
- ✅ Soft deletes para auditoría
- ✅ Permisos diferenciados por rol

