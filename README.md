# Proyecto_Api_Forneria
Objetivo
Desarrollar una aplicación Django compuesta por dos apps: Inventario y Ventas, con entrega final el 20 de noviembre. El trabajo se dividirá entre backend y templates para optimizar tiempos.

División del Equipo


Backend (2 personas):

Persona 1: App Inventario → Modelos, vistas, CRUD, conexión MySQL.
Persona 2: App Ventas → Modelos, vistas, CRUD, conexión MySQL.



Templates (2 personas):

Persona 3: Templates para Inventario → Listado, formularios, estilos.
Persona 4: Templates para Ventas → Listado, formularios, layout base.




Estructura del Proyecto
PROYECTO_API_FORNERIA/
│
├── apps/
│   ├── inventario/
│   ├── ventas/
├── templates/
│   ├── inventario/
│   ├── ventas/
│   ├── base.html
├── static/
├── manage.py
├── requirements.txt
└── README.md

Plan de Trabajo

13-16: Desarrollo paralelo (backend y templates).
17: Integración parcial y pruebas.
18-19: Ajustes, validaciones, documentación.
20: Entrega final.

Ejemplo Backend (Inventario)


 apps/inventario/models.py
from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    
Vista básica:

# apps/inventario/views.py
from django.shortcuts import render
from .models import Producto

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'inventario/lista.html', {'productos': productos})
    
Buenas Prácticas

Usar ramas por funcionalidad:
feature/inventario-backend, feature/ventas-backend, feature/inventario-templates, feature/ventas-templates.
Documentar en README.md cómo instalar y correr el proyecto.
Comunicación diaria breve para sincronizar avances.
