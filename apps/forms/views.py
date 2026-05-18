from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import FileResponse
from datetime import date
import json
from django.core.serializers.json import DjangoJSONEncoder

from .models import (
    Asignacion, AsignacionDetalle, Prestamo, Devolucion,
    generar_codigo, COMPONENTES_PC, COMPONENTES_LAPTOP,
    COMPONENTES_IMPRESORA, COMPONENTES_PERIFERICOS,
)
from .pdf_utils import generar_pdf_asignacion
from .forms import AsignacionForm, PrestamoForm, DevolucionForm
from apps.equipment.models import Equipment, EquipmentCategory
from apps.employees.models import Employee

TIPO_SECTIONS = [
    ('pc', 'PC', COMPONENTES_PC),
    ('laptop', 'Laptop', COMPONENTES_LAPTOP),
    ('impresora', 'Impresora', COMPONENTES_IMPRESORA),
    ('perifericos', 'Perifericos', COMPONENTES_PERIFERICOS),
]


def _employees_json():
    qs = Employee.objects.filter(activo=True).values('id', 'nombre', 'apellido', 'cedula', 'cargo', 'departamento')
    return json.dumps(list(qs), cls=DjangoJSONEncoder)


def _build_componentes(post, tipo):
    nombres = post.getlist(f'comp_nombre_{tipo}')
    marcas = post.getlist(f'comp_marca_{tipo}')
    modelos = post.getlist(f'comp_modelo_{tipo}')
    series = post.getlist(f'comp_serie_{tipo}')
    estados = post.getlist(f'comp_estado_{tipo}')

    result = []
    for i in range(len(nombres)):
        if tipo == 'pc':
            capacidades = post.getlist(f'comp_capacidad_{tipo}')
            item = {'nombre': nombres[i], 'marca': marcas[i].strip(), 'modelo': modelos[i].strip(),
                    'capacidad': capacidades[i].strip() if i < len(capacidades) else '',
                    'serie': series[i].strip(), 'estado': estados[i].strip()}
            if item['marca'] or item['modelo'] or item['capacidad'] or item['serie']:
                result.append(item)
        elif tipo == 'laptop':
            ssds = post.getlist(f'comp_ssd_{tipo}')
            hdds = post.getlist(f'comp_hdd_{tipo}')
            memorias = post.getlist(f'comp_memoria_ram_{tipo}')
            item = {'nombre': nombres[i], 'marca': marcas[i].strip() if i < len(marcas) else '',
                    'modelo': modelos[i].strip() if i < len(modelos) else '',
                    'ssd': ssds[i].strip() if i < len(ssds) else '',
                    'hdd': hdds[i].strip() if i < len(hdds) else '',
                    'memoria_ram': memorias[i].strip() if i < len(memorias) else '',
                    'serie': series[i].strip() if i < len(series) else '',
                    'estado': estados[i].strip() if i < len(estados) else ''}
            if item['marca'] or item['modelo'] or item['ssd'] or item['hdd'] or item['memoria_ram'] or item['serie']:
                result.append(item)
        else:
            item = {'nombre': nombres[i], 'marca': marcas[i].strip(), 'modelo': modelos[i].strip(),
                    'serie': series[i].strip(), 'estado': estados[i].strip()}
            if item['marca'] or item['modelo'] or item['serie']:
                result.append(item)
    return result


@login_required
def index(request):
    return render(request, 'forms/index.html', {
        'asignaciones': Asignacion.objects.count(),
        'prestamos': Prestamo.objects.count(),
        'devoluciones': Devolucion.objects.count(),
        'prestamos_activos': Prestamo.objects.filter(estado='activo').count(),
    })


@login_required
def formatos(request):
    return render(request, 'forms/formatos.html')


@login_required
def asignacion_create(request):
    today_lima = date.today()

    if request.method == 'POST':
        post = request.POST.copy()
        employee_id = post.get('employee_id', '')
        if employee_id:
            post['employee'] = employee_id
        post['fecha_asignacion'] = today_lima.isoformat()
        tipos = post.getlist('tipo_equipo')
        post['tipo_equipo'] = tipos[0] if tipos else 'pc'
        form = AsignacionForm(post)

        if form.is_valid():
            asignacion = form.save(commit=False)
            asignacion.codigo = generar_codigo(Asignacion, 'ASI')
            asignacion.created_by = request.user
            asignacion.save()

            for idx, tipo in enumerate(tipos, 1):
                componentes = _build_componentes(post, tipo)
                cat, _ = EquipmentCategory.objects.get_or_create(nombre=tipo.capitalize())
                equipo = Equipment.objects.create(
                    codigo_patrimonial=f'{asignacion.codigo}-{idx:02d}',
                    categoria=cat,
                    marca=componentes[0]['marca'] if componentes else '',
                    modelo=componentes[0]['modelo'] if componentes else '',
                    numero_serie=componentes[0]['serie'] if componentes else '',
                    estado='asignado',
                    ubicacion=asignacion.employee.departamento,
                )
                AsignacionDetalle.objects.create(
                    asignacion=asignacion, equipment=equipo,
                    tipo_equipo=tipo, estado_entrega='bueno',
                    componentes_data=componentes,
                )

            messages.success(request, f'Acta {asignacion.codigo} creada exitosamente.')
            return redirect('forms:asignacion_list')
    else:
        form = AsignacionForm()

    form.initial['fecha_asignacion'] = today_lima
    return render(request, 'forms/asignacion_form.html', {
        'form': form,
        'titulo': 'Nueva Acta de Asignacion',
        'codigo_siguiente': generar_codigo(Asignacion, 'ASI'),
        'fecha_actual': today_lima.isoformat(),
        'tipo_sections': TIPO_SECTIONS,
        'employees_json': _employees_json(),
        'responsable_nombre': request.user.get_full_name() or request.user.username,
    })


@login_required
def asignacion_list(request):
    return render(request, 'forms/asignacion_list.html', {
        'asignaciones': Asignacion.objects.all().select_related('employee', 'created_by'),
    })


@login_required
def asignacion_detail(request, pk):
    asignacion = get_object_or_404(Asignacion.objects.select_related('employee', 'created_by'), pk=pk)
    return render(request, 'forms/asignacion_detail.html', {
        'asignacion': asignacion,
        'detalles': asignacion.detalles.all().select_related('equipment'),
    })


@login_required
def asignacion_edit(request, pk):
    asignacion = get_object_or_404(Asignacion, pk=pk)
    detalles = asignacion.detalles.all()

    if request.method == 'POST':
        post = request.POST.copy()
        employee_id = post.get('employee_id', '')
        if employee_id:
            post['employee'] = employee_id
        post['fecha_asignacion'] = asignacion.fecha_asignacion.isoformat()
        tipos = post.getlist('tipo_equipo')
        post['tipo_equipo'] = tipos[0] if tipos else 'pc'
        form = AsignacionForm(post, instance=asignacion)
        if form.is_valid():
            form.save()
            tipos_existentes = set(d.tipo_equipo for d in detalles)
            tipos_nuevos = set(tipos)

            for idx, tipo in enumerate(tipos, 1):
                componentes = _build_componentes(post, tipo)
                cat, _ = EquipmentCategory.objects.get_or_create(nombre=tipo.capitalize())

                if tipo in tipos_existentes:
                    detalle = detalles.get(tipo_equipo=tipo)
                    equipo = detalle.equipment
                    equipo.marca = componentes[0]['marca'] if componentes else equipo.marca
                    equipo.modelo = componentes[0]['modelo'] if componentes else equipo.modelo
                    equipo.numero_serie = componentes[0]['serie'] if componentes else equipo.numero_serie
                    equipo.save()
                    detalle.componentes_data = componentes
                    detalle.save()
                else:
                    equipo = Equipment.objects.create(
                        codigo_patrimonial=f'{asignacion.codigo}-{idx:02d}',
                        categoria=cat,
                        marca=componentes[0]['marca'] if componentes else '',
                        modelo=componentes[0]['modelo'] if componentes else '',
                        numero_serie=componentes[0]['serie'] if componentes else '',
                        estado='asignado',
                        ubicacion=asignacion.employee.departamento,
                    )
                    AsignacionDetalle.objects.create(
                        asignacion=asignacion, equipment=equipo,
                        tipo_equipo=tipo, estado_entrega='bueno',
                        componentes_data=componentes,
                    )

            for tipo in (tipos_existentes - tipos_nuevos):
                detalle = detalles.get(tipo_equipo=tipo)
                detalle.equipment.delete()
                detalle.delete()

            messages.success(request, f'Acta {asignacion.codigo} actualizada.')
            return redirect('forms:asignacion_detail', pk=asignacion.pk)
    else:
        form = AsignacionForm(instance=asignacion)

    detalles = asignacion.detalles.all()
    componentes_existentes = {d.tipo_equipo: d.componentes_data or [] for d in detalles}
    tipos_seleccionados = list(componentes_existentes.keys())
    empleados_list = json.loads(_employees_json())
    emp_asignacion = {
        'id': asignacion.employee.id,
        'nombre': asignacion.employee.nombre,
        'apellido': asignacion.employee.apellido,
        'cedula': asignacion.employee.cedula,
        'cargo': asignacion.employee.cargo,
        'departamento': asignacion.employee.departamento,
    }
    if not any(e['id'] == emp_asignacion['id'] for e in empleados_list):
        empleados_list.insert(0, emp_asignacion)

    return render(request, 'forms/asignacion_form.html', {
        'form': form,
        'titulo': f'Editar {asignacion.codigo}',
        'edit_mode': True,
        'asignacion': asignacion,
        'codigo_siguiente': asignacion.codigo,
        'fecha_actual': asignacion.fecha_asignacion.isoformat(),
        'tipo_sections': TIPO_SECTIONS,
        'employees_json': json.dumps(empleados_list, cls=DjangoJSONEncoder),
        'componentes_json': json.dumps(componentes_existentes, cls=DjangoJSONEncoder),
        'tipos_seleccionados': tipos_seleccionados,
        'detalles_map': {d.tipo_equipo: d.pk for d in detalles},
        'equipos_map': {d.tipo_equipo: d.equipment.pk for d in detalles},
        'responsable_nombre': request.user.get_full_name() or request.user.username,
    })


@login_required
def asignacion_delete(request, pk):
    asignacion = get_object_or_404(Asignacion, pk=pk)
    if request.method == 'POST':
        codigo = asignacion.codigo
        asignacion.delete()
        messages.success(request, f'Acta {codigo} eliminada.')
        return redirect('forms:asignacion_list')
    return render(request, 'forms/asignacion_confirm_delete.html', {'asignacion': asignacion})


@login_required
def prestamo_create(request):
    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        if form.is_valid():
            prestamo = form.save(commit=False)
            prestamo.codigo = generar_codigo(Prestamo, 'PRE')
            prestamo.created_by = request.user
            prestamo.save()
            messages.success(request, f'Acta {prestamo.codigo} creada.')
            return redirect('forms:prestamo_list')
    else:
        form = PrestamoForm()
    return render(request, 'forms/prestamo_form.html', {'form': form, 'titulo': 'Nuevo Acta de Prestamo'})


@login_required
def prestamo_list(request):
    return render(request, 'forms/prestamo_list.html', {
        'prestamos': Prestamo.objects.all().select_related('employee', 'created_by'),
    })


@login_required
def prestamo_detail(request, pk):
    prestamo = get_object_or_404(Prestamo.objects.select_related('employee', 'created_by'), pk=pk)
    return render(request, 'forms/prestamo_detail.html', {
        'prestamo': prestamo,
        'detalles': prestamo.detalles.all().select_related('equipment'),
    })


@login_required
def devolucion_create(request):
    if request.method == 'POST':
        form = DevolucionForm(request.POST)
        if form.is_valid():
            devolucion = form.save(commit=False)
            devolucion.codigo = generar_codigo(Devolucion, 'DEV')
            devolucion.created_by = request.user
            devolucion.save()
            messages.success(request, f'Acta {devolucion.codigo} creada.')
            return redirect('forms:devolucion_list')
    else:
        form = DevolucionForm()
    return render(request, 'forms/devolucion_form.html', {'form': form, 'titulo': 'Nueva Acta de Devolucion'})


@login_required
def devolucion_list(request):
    return render(request, 'forms/devolucion_list.html', {
        'devoluciones': Devolucion.objects.all().select_related('employee', 'created_by'),
    })


@login_required
def devolucion_detail(request, pk):
    devolucion = get_object_or_404(Devolucion.objects.select_related('employee', 'created_by'), pk=pk)
    return render(request, 'forms/devolucion_detail.html', {
        'devolucion': devolucion,
        'detalles': devolucion.detalles.all().select_related('equipment'),
    })


@login_required
def asignacion_pdf(request, pk):
    asignacion = get_object_or_404(Asignacion.objects.select_related('employee', 'created_by'), pk=pk)
    buffer = generar_pdf_asignacion(asignacion, request)
    return FileResponse(buffer, as_attachment=True, filename=f'{asignacion.codigo}.pdf')
