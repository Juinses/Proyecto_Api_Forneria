# inventario/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('', views.inventario_home, name='inventario_home'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('nuevo/', views.crear_producto, name='crear_producto'),
    path('editar/<int:pk>/', views.editar_producto, name='editar_producto'),       
    path('eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'), 
    path('movimientos/', views.movimientos_inventario, name='movimientos_inventario'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/nueva/', views.crear_categoria, name='crear_categoria'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),
    path('nutricional/nuevo/', views.crear_nutricional, name='crear_nutricional'),
]
