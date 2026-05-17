from django.db import models

class EquipmentCategory(models.Model):
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    descripcion = models.TextField('Descripcion', blank=True)

    class Meta:
        verbose_name = 'Categoria de Equipo'
        verbose_name_plural = 'Categorias de Equipos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Equipment(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('asignado', 'Asignado'),
        ('prestado', 'Prestado'),
        ('en_reparacion', 'En Reparacion'),
        ('dado_baja', 'Dado de Baja'),
    ]

    codigo_patrimonial = models.CharField('Codigo Patrimonial', max_length=50, unique=True)
    categoria = models.ForeignKey(EquipmentCategory, on_delete=models.PROTECT, verbose_name='Categoria')
    marca = models.CharField('Marca', max_length=100)
    modelo = models.CharField('Modelo', max_length=100)
    numero_serie = models.CharField('Numero de Serie', max_length=100, unique=True)
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='disponible')
    ubicacion = models.CharField('Ubicacion', max_length=200, blank=True)
    observaciones = models.TextField('Observaciones', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['codigo_patrimonial']

    def __str__(self):
        return f"{self.codigo_patrimonial} - {self.marca} {self.modelo} ({self.get_estado_display()})"
