from django.urls import path
from . import views

urlpatterns = [
    path('', views.ventas_home, name='ventas_home'),
    path('listado/', views.lista_ventas, name='lista_ventas'),
    path('nuevo/', views.crear_venta, name='crear_venta'),
    path('editar/<int:venta_id>/', views.editar_venta, name='editar_venta'),
    path('eliminar/<int:venta_id>/', views.eliminar_venta, name='eliminar_venta'),
    path('comprobante/<int:venta_id>/', views.comprobante_html, name='comprobante_html'),
    path('comprobante/<int:venta_id>/pdf/', views.comprobante_pdf, name='comprobante_pdf'),
]