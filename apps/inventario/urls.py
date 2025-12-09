from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventario_home, name='inventario_home'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('nuevo/', views.crear_producto, name='crear_producto'),
    path('editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('movimientos/', views.movimientos_inventario, name='movimientos_inventario'),
]
