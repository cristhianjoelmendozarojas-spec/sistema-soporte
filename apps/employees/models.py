from django.db import models

class Employee(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    apellido = models.CharField('Apellido', max_length=100)
    cedula = models.CharField('Cedula / DNI', max_length=20, unique=True)
    cargo = models.CharField('Cargo', max_length=150)
    departamento = models.CharField('Departamento', max_length=150)
    telefono = models.CharField('Telefono', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    activo = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.apellido}, {self.nombre} - {self.cedula}"
