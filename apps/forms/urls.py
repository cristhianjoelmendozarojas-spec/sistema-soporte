from django.urls import path
from . import views

app_name = 'forms'

urlpatterns = [
    path('', views.index, name='index'),
    path('formatos/', views.formatos, name='formatos'),
    path('asignaciones/', views.asignacion_list, name='asignacion_list'),
    path('asignaciones/nueva/', views.asignacion_create, name='asignacion_create'),
    path('asignaciones/<int:pk>/', views.asignacion_detail, name='asignacion_detail'),
    path('asignaciones/<int:pk>/editar/', views.asignacion_edit, name='asignacion_edit'),
    path('asignaciones/<int:pk>/eliminar/', views.asignacion_delete, name='asignacion_delete'),
    path('asignaciones/<int:pk>/pdf/', views.asignacion_pdf, name='asignacion_pdf'),
    path('prestamos/', views.prestamo_list, name='prestamo_list'),
    path('prestamos/nuevo/', views.prestamo_create, name='prestamo_create'),
    path('prestamos/<int:pk>/', views.prestamo_detail, name='prestamo_detail'),
    path('devoluciones/', views.devolucion_list, name='devolucion_list'),
    path('devoluciones/nueva/', views.devolucion_create, name='devolucion_create'),
    path('devoluciones/<int:pk>/', views.devolucion_detail, name='devolucion_detail'),
]
