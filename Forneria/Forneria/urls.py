from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView


urlpatterns = [
    path('', RedirectView.as_view(url='/ventas/', permanent=False), name='index'),
    path('admin/',admin.site.urls),
    path('inventario/', include('apps.inventario.urls')),
    path('ventas/', include('apps.ventas.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
