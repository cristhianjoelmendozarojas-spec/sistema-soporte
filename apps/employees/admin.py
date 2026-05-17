from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['apellido', 'nombre', 'cedula', 'cargo', 'departamento', 'activo']
    list_filter = ['activo', 'departamento']
    search_fields = ['nombre', 'apellido', 'cedula', 'cargo', 'departamento']
    list_editable = ['activo']
