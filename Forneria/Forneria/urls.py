from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('admin/',admin.site.urls),
    path('inventario/', include('apps.inventario.urls')),
    path('ventas/', include('apps.ventas.urls')),
    path('', include(router.urls)),
]
