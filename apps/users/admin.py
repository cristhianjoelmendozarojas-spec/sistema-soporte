from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'

class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'get_rol']

    def get_rol(self, obj):
        return obj.profile.get_rol_display()
    get_rol.short_description = 'Rol'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
