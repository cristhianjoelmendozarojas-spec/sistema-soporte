from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Asignacion, Prestamo, Devolucion
from .forms import (
    AsignacionForm, AsignacionDetalleForm,
    PrestamoForm, PrestamoDetalleForm,
    DevolucionForm, DevolucionDetalleForm,
)


@login_required
def index(request):
    context = {
        'asignaciones': Asignacion.objects.count(),
        'prestamos': Prestamo.objects.count(),
        'devoluciones': Devolucion.objects.count(),
        'prestamos_activos': Prestamo.objects.filter(estado='activo').count(),
    }
    return render(request, 'forms/index.html', context)


@login_required
@permission_required('forms.add_asignacion', raise_exception=True)
def asignacion_create(request):
    if request.method == 'POST':
        form = AsignacionForm(request.POST)
        if form.is_valid():
            asignacion = form.save(commit=False)
            asignacion.created_by = request.user
            asignacion.save()
            messages.success(request, f'Acta de asignacion {asignacion.codigo} creada exitosamente.')
            return redirect('forms:asignacion_list')
    else:
        form = AsignacionForm()
    return render(request, 'forms/asignacion_form.html', {'form': form, 'titulo': 'Nueva Acta de Asignacion'})


@login_required
def asignacion_list(request):
    asignaciones = Asignacion.objects.all().select_related('employee', 'created_by')
    return render(request, 'forms/asignacion_list.html', {'asignaciones': asignaciones})


@login_required
def asignacion_detail(request, pk):
    asignacion = get_object_or_404(Asignacion.objects.select_related('employee', 'created_by'), pk=pk)
    detalles = asignacion.detalles.all().select_related('equipment')
    return render(request, 'forms/asignacion_detail.html', {'asignacion': asignacion, 'detalles': detalles})


@login_required
@permission_required('forms.add_prestamo', raise_exception=True)
def prestamo_create(request):
    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        if form.is_valid():
            prestamo = form.save(commit=False)
            prestamo.created_by = request.user
            prestamo.save()
            messages.success(request, f'Acta de prestamo {prestamo.codigo} creada exitosamente.')
            return redirect('forms:prestamo_list')
    else:
        form = PrestamoForm()
    return render(request, 'forms/prestamo_form.html', {'form': form, 'titulo': 'Nuevo Acta de Prestamo'})


@login_required
def prestamo_list(request):
    prestamos = Prestamo.objects.all().select_related('employee', 'created_by')
    return render(request, 'forms/prestamo_list.html', {'prestamos': prestamos})


@login_required
def prestamo_detail(request, pk):
    prestamo = get_object_or_404(Prestamo.objects.select_related('employee', 'created_by'), pk=pk)
    detalles = prestamo.detalles.all().select_related('equipment')
    return render(request, 'forms/prestamo_detail.html', {'prestamo': prestamo, 'detalles': detalles})


@login_required
@permission_required('forms.add_devolucion', raise_exception=True)
def devolucion_create(request):
    if request.method == 'POST':
        form = DevolucionForm(request.POST)
        if form.is_valid():
            devolucion = form.save(commit=False)
            devolucion.created_by = request.user
            devolucion.save()
            messages.success(request, f'Acta de devolucion {devolucion.codigo} creada exitosamente.')
            return redirect('forms:devolucion_list')
    else:
        form = DevolucionForm()
    return render(request, 'forms/devolucion_form.html', {'form': form, 'titulo': 'Nueva Acta de Devolucion'})


@login_required
def devolucion_list(request):
    devoluciones = Devolucion.objects.all().select_related('employee', 'created_by')
    return render(request, 'forms/devolucion_list.html', {'devoluciones': devoluciones})


@login_required
def devolucion_detail(request, pk):
    devolucion = get_object_or_404(Devolucion.objects.select_related('employee', 'created_by'), pk=pk)
    detalles = devolucion.detalles.all().select_related('equipment')
    return render(request, 'forms/devolucion_detail.html', {'devolucion': devolucion, 'detalles': detalles})
