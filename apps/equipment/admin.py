from django.contrib import admin
from .models import EquipmentCategory, Equipment

@admin.register(EquipmentCategory)
class EquipmentCategoryAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['codigo_patrimonial', 'categoria', 'marca', 'modelo', 'numero_serie', 'estado', 'ubicacion']
    list_filter = ['estado', 'categoria']
    search_fields = ['codigo_patrimonial', 'marca', 'modelo', 'numero_serie']
    list_editable = ['estado']
