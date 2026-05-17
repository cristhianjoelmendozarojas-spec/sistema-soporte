from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.conf import settings
import base64, uuid, os
from .models import Profile, Module, Firma, tiene_privilegios_admin


def _es_admin(user):
    return tiene_privilegios_admin(user)


@login_required
def user_list(request):
    if not _es_admin(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta seccion.')
        return redirect('forms:index')
    users = User.objects.all().select_related('profile')
    return render(request, 'users/user_list.html', {'users': users})


@login_required
def user_create(request):
    if not _es_admin(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta seccion.')
        return redirect('forms:index')

    if request.method == 'POST':
        dni = request.POST.get('dni', '').strip()
        email = request.POST.get('email', '')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        rol = request.POST.get('rol', 'standard')
        modulos_ids = request.POST.getlist('modulos')

        if not dni:
            messages.error(request, 'El DNI es obligatorio.')
        elif len(dni) < 6:
            messages.error(request, 'El DNI debe tener al menos 6 caracteres.')
        elif User.objects.filter(username=dni).exists():
            messages.error(request, f'El DNI "{dni}" ya esta registrado.')
        elif not password:
            messages.error(request, 'La contrasena es obligatoria.')
        else:
            user = User.objects.create(
                username=dni,
                email=email,
                password=make_password(password),
                first_name=first_name,
                last_name=last_name,
            )
            profile = user.profile
            profile.rol = rol
            profile.cambiar_password = True
            profile.save()
            if modulos_ids:
                profile.modulos.set(Module.objects.filter(id__in=modulos_ids))
            messages.success(request, f'Usuario con DNI "{dni}" creado exitosamente. Debera cambiar su contrasena al iniciar sesion.')
            return redirect('users:user_list')

    modulos = Module.objects.filter(activo=True)
    return render(request, 'users/user_form.html', {
        'titulo': 'Nuevo Usuario',
        'modulos': modulos,
        'user_obj': None,
    })


@login_required
def user_edit(request, pk):
    if not _es_admin(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta seccion.')
        return redirect('forms:index')

    user_obj = get_object_or_404(User.objects.select_related('profile'), pk=pk)

    if request.method == 'POST':
        user_obj.email = request.POST.get('email', '')
        user_obj.first_name = request.POST.get('first_name', '')
        user_obj.last_name = request.POST.get('last_name', '')
        password = request.POST.get('password', '')
        if password:
            user_obj.password = make_password(password)
            user_obj.profile.cambiar_password = True
        user_obj.save()

        profile = user_obj.profile
        profile.rol = request.POST.get('rol', 'standard')
        profile.cambiar_password = request.POST.get('cambiar_password') == 'on'
        profile.save()

        modulos_ids = request.POST.getlist('modulos')
        profile.modulos.set(Module.objects.filter(id__in=modulos_ids))

        messages.success(request, f'Usuario "{user_obj.username}" actualizado exitosamente.')
        return redirect('users:user_list')

    modulos = Module.objects.filter(activo=True)
    user_modulos_ids = list(user_obj.profile.modulos.values_list('id', flat=True))
    return render(request, 'users/user_form.html', {
        'titulo': 'Editar Usuario',
        'modulos': modulos,
        'user_obj': user_obj,
        'user_modulos_ids': user_modulos_ids,
    })


@login_required
def user_delete(request, pk):
    if not _es_admin(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta seccion.')
        return redirect('forms:index')

    user_obj = get_object_or_404(User, pk=pk)
    if user_obj == request.user:
        messages.error(request, 'No puedes eliminarte a ti mismo.')
        return redirect('users:user_list')

    if request.method == 'POST':
        dni = user_obj.username
        user_obj.delete()
        messages.success(request, f'Usuario con DNI "{dni}" eliminado exitosamente.')
        return redirect('users:user_list')

    return render(request, 'users/user_confirm_delete.html', {'user_obj': user_obj})


@login_required
def cambiar_password(request):
    profile = request.user.profile
    if request.method == 'POST':
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        if not password1:
            messages.error(request, 'La contrasena es obligatoria.')
        elif password1 != password2:
            messages.error(request, 'Las contrasenas no coinciden.')
        elif len(password1) < 4:
            messages.error(request, 'La contrasena debe tener al menos 4 caracteres.')
        else:
            request.user.set_password(password1)
            request.user.save()
            profile.cambiar_password = False
            profile.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Contrasena cambiada exitosamente.')
            return redirect('forms:index')
    return render(request, 'users/cambiar_password.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('forms:index')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido {user.get_full_name() or user.username}')
            return redirect('forms:index')
        else:
            messages.error(request, 'DNI o contrasena incorrectos.')
    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Sesion cerrada exitosamente.')
    return redirect('users:login')


@login_required
def firma_view(request):
    firma, created = Firma.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        modo = request.POST.get('modo', '')

        if modo == 'imagen' and request.FILES.get('imagen'):
            firma.imagen = request.FILES['imagen']
            firma.datos_firma = ''
            firma.save()
            messages.success(request, 'Imagen de firma subida exitosamente.')
            return redirect('users:firma')

        elif modo == 'canvas':
            data_url = request.POST.get('datos_firma', '')
            if data_url:
                firma.datos_firma = data_url
                if firma.imagen:
                    firma.imagen.delete(save=False)
                    firma.imagen = None
                firma.save()
                messages.success(request, 'Firma dibujada guardada exitosamente.')
                return redirect('users:firma')

        messages.error(request, 'No se pudo guardar la firma.')

    return render(request, 'users/firma.html', {'firma': firma})
