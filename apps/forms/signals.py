from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import AsignacionDetalle, PrestamoDetalle, DevolucionDetalle
from apps.equipment.models import Equipment


@receiver(post_save, sender=AsignacionDetalle)
def asignar_equipo(sender, instance, created, **kwargs):
    if created:
        equipo = instance.equipment
        equipo.estado = 'asignado'
        equipo.save()


@receiver(post_delete, sender=AsignacionDetalle)
def liberar_equipo_asignacion(sender, instance, **kwargs):
    equipo = instance.equipment
    if equipo.estado == 'asignado':
        equipo.estado = 'disponible'
        equipo.save()


@receiver(post_save, sender=PrestamoDetalle)
def prestar_equipo(sender, instance, created, **kwargs):
    if created:
        equipo = instance.equipment
        equipo.estado = 'prestado'
        equipo.save()


@receiver(post_save, sender=DevolucionDetalle)
def devolver_equipo(sender, instance, created, **kwargs):
    if created:
        equipo = instance.equipment
        equipo.estado = 'disponible'
        equipo.save()
