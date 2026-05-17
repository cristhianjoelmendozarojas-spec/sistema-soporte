from django.db import models
from django.contrib.auth.models import User
from apps.employees.models import Employee
from apps.equipment.models import Equipment


class Asignacion(models.Model):
    codigo = models.CharField('Codigo de Acta', max_length=50, unique=True)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name='Empleado')
    fecha_asignacion = models.DateField('Fecha de Asignacion')
    motivo = models.TextField('Motivo')
    observaciones = models.TextField('Observaciones', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Acta de Asignacion'
        verbose_name_plural = 'Actas de Asignacion'
        ordering = ['-fecha_asignacion']

    def __str__(self):
        return f"{self.codigo} - {self.employee}"


class AsignacionDetalle(models.Model):
    ESTADO_EQUIPO_CHOICES = [
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('malo', 'Malo'),
    ]

    asignacion = models.ForeignKey(Asignacion, on_delete=models.CASCADE, related_name='detalles', verbose_name='Asignacion')
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, verbose_name='Equipo')
    estado_entrega = models.CharField('Estado de Entrega', max_length=20, choices=ESTADO_EQUIPO_CHOICES)
    observaciones = models.TextField('Observaciones', blank=True)

    class Meta:
        verbose_name = 'Detalle de Asignacion'
        verbose_name_plural = 'Detalles de Asignacion'

    def __str__(self):
        return f"{self.asignacion.codigo} - {self.equipment}"


class Prestamo(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('vencido', 'Vencido'),
        ('devuelto', 'Devuelto'),
        ('cancelado', 'Cancelado'),
    ]

    codigo = models.CharField('Codigo de Acta', max_length=50, unique=True)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name='Empleado')
    fecha_prestamo = models.DateField('Fecha de Prestamo')
    fecha_prevista_devolucion = models.DateField('Fecha Prevista de Devolucion')
    motivo = models.TextField('Motivo')
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='activo')
    observaciones = models.TextField('Observaciones', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Acta de Prestamo'
        verbose_name_plural = 'Actas de Prestamo'
        ordering = ['-fecha_prestamo']

    def __str__(self):
        return f"{self.codigo} - {self.employee} ({self.get_estado_display()})"


class PrestamoDetalle(models.Model):
    ESTADO_EQUIPO_CHOICES = [
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('malo', 'Malo'),
    ]

    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, related_name='detalles', verbose_name='Prestamo')
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, verbose_name='Equipo')
    estado_entrega = models.CharField('Estado de Entrega', max_length=20, choices=ESTADO_EQUIPO_CHOICES)
    fecha_devolucion = models.DateField('Fecha de Devolucion', null=True, blank=True)
    estado_devolucion = models.CharField('Estado de Devolucion', max_length=20, choices=ESTADO_EQUIPO_CHOICES, null=True, blank=True)
    observaciones_devolucion = models.TextField('Observaciones de Devolucion', blank=True)

    class Meta:
        verbose_name = 'Detalle de Prestamo'
        verbose_name_plural = 'Detalles de Prestamo'

    def __str__(self):
        return f"{self.prestamo.codigo} - {self.equipment}"


class Devolucion(models.Model):
    codigo = models.CharField('Codigo de Acta', max_length=50, unique=True)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name='Empleado')
    asignacion = models.ForeignKey(Asignacion, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Asignacion relacionada')
    prestamo = models.ForeignKey(Prestamo, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Prestamo relacionado')
    fecha_devolucion = models.DateField('Fecha de Devolucion')
    observaciones = models.TextField('Observaciones', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Acta de Devolucion'
        verbose_name_plural = 'Actas de Devolucion'
        ordering = ['-fecha_devolucion']

    def __str__(self):
        return f"{self.codigo} - {self.employee}"


class DevolucionDetalle(models.Model):
    ESTADO_EQUIPO_CHOICES = [
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('malo', 'Malo'),
    ]

    devolucion = models.ForeignKey(Devolucion, on_delete=models.CASCADE, related_name='detalles', verbose_name='Devolucion')
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, verbose_name='Equipo')
    estado_recibido = models.CharField('Estado Recibido', max_length=20, choices=ESTADO_EQUIPO_CHOICES)
    observaciones = models.TextField('Observaciones', blank=True)

    class Meta:
        verbose_name = 'Detalle de Devolucion'
        verbose_name_plural = 'Detalles de Devolucion'

    def __str__(self):
        return f"{self.devolucion.codigo} - {self.equipment}"
