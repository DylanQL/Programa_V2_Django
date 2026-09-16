from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('funcionalidad-1/', views.ejecutar_funcionalidad_1, name='func1'),
    path('funcionalidad-2/', views.ejecutar_funcionalidad_2, name='func2'),
]
