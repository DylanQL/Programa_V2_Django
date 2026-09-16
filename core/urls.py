from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Esto hace que la página principal de tu dominio cargue directamente tu app
    path('', include('parser_app.urls')), 
]
