from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('standard', 'Estandar'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rol = models.CharField('Rol', max_length=20, choices=ROL_CHOICES, default='standard')
    telefono = models.CharField('Telefono', max_length=20, blank=True)
    area = models.CharField('Area', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_rol_display()}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
