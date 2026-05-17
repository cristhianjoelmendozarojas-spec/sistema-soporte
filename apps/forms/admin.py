from django.contrib import admin
from .models import (
    Asignacion, AsignacionDetalle,
    Prestamo, PrestamoDetalle,
    Devolucion, DevolucionDetalle,
)


class AsignacionDetalleInline(admin.TabularInline):
    model = AsignacionDetalle
    extra = 1
    autocomplete_fields = ['equipment']


@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'employee', 'fecha_asignacion', 'created_by', 'created_at']
    list_filter = ['fecha_asignacion']
    search_fields = ['codigo', 'employee__nombre', 'employee__apellido', 'employee__cedula']
    autocomplete_fields = ['employee', 'created_by']
    inlines = [AsignacionDetalleInline]
    date_hierarchy = 'fecha_asignacion'


class PrestamoDetalleInline(admin.TabularInline):
    model = PrestamoDetalle
    extra = 1
    autocomplete_fields = ['equipment']


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'employee', 'fecha_prestamo', 'fecha_prevista_devolucion', 'estado', 'created_by']
    list_filter = ['estado', 'fecha_prestamo']
    search_fields = ['codigo', 'employee__nombre', 'employee__apellido', 'employee__cedula']
    autocomplete_fields = ['employee', 'created_by']
    inlines = [PrestamoDetalleInline]
    date_hierarchy = 'fecha_prestamo'


class DevolucionDetalleInline(admin.TabularInline):
    model = DevolucionDetalle
    extra = 1
    autocomplete_fields = ['equipment']


@admin.register(Devolucion)
class DevolucionAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'employee', 'fecha_devolucion', 'asignacion', 'prestamo', 'created_by']
    list_filter = ['fecha_devolucion']
    search_fields = ['codigo', 'employee__nombre', 'employee__apellido', 'employee__cedula']
    autocomplete_fields = ['employee', 'asignacion', 'prestamo', 'created_by']
    inlines = [DevolucionDetalleInline]
    date_hierarchy = 'fecha_devolucion'
