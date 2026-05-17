from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('nuevo/', views.employee_create, name='employee_create'),
    path('<int:pk>/editar/', views.employee_edit, name='employee_edit'),
    path('<int:pk>/eliminar/', views.employee_delete, name='employee_delete'),
    path('ajax/crear/', views.employee_create_ajax, name='employee_create_ajax'),
]
