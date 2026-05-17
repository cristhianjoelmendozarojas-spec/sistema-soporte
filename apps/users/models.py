from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Module(models.Model):
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    icono = models.CharField('Icono', max_length=20, blank=True)
    url_name = models.CharField('URL Name', max_length=100, blank=True)
    activo = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Modulo'
        verbose_name_plural = 'Modulos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Profile(models.Model):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('standard', 'Estandar'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rol = models.CharField('Rol', max_length=20, choices=ROL_CHOICES, default='standard')
    telefono = models.CharField('Telefono', max_length=20, blank=True)
    area = models.CharField('Area', max_length=100, blank=True)
    modulos = models.ManyToManyField(Module, blank=True, verbose_name='Modulos asignados')
    cambiar_password = models.BooleanField('Cambiar password', default=True,
        help_text='Si esta activo, el usuario debera cambiar su contrasena al iniciar sesion')

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_rol_display()}"


def tiene_privilegios_admin(user):
    return user.is_superuser or user.is_staff or user.profile.rol == 'admin'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Firma(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='firma')
    imagen = models.ImageField('Imagen de Firma', upload_to='firmas/', blank=True, null=True)
    datos_firma = models.TextField('Datos de Firma (base64)', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Firma'
        verbose_name_plural = 'Firmas'

    def __str__(self):
        return f'Firma de {self.user.get_full_name() or self.user.username}'


@receiver(post_save, sender=User)
def create_user_firma(sender, instance, created, **kwargs):
    if created:
        Firma.objects.get_or_create(user=instance)
