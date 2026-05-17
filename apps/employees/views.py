from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Employee


@login_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employees/employee_list.html', {'employees': employees})


@login_required
def employee_create(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        cedula = request.POST.get('cedula', '').strip()
        cargo = request.POST.get('cargo', '').strip()
        departamento = request.POST.get('departamento', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email = request.POST.get('email', '').strip()

        errors = []
        if not nombre:
            errors.append('El nombre es obligatorio.')
        if not apellido:
            errors.append('El apellido es obligatorio.')
        if not cedula:
            errors.append('La cedula es obligatoria.')
        elif Employee.objects.filter(cedula=cedula).exists():
            errors.append(f'La cedula "{cedula}" ya esta registrada.')
        if not cargo:
            errors.append('El cargo es obligatorio.')
        if not departamento:
            errors.append('El departamento es obligatorio.')

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            Employee.objects.create(
                nombre=nombre,
                apellido=apellido,
                cedula=cedula,
                cargo=cargo,
                departamento=departamento,
                telefono=telefono,
                email=email,
            )
            messages.success(request, f'Colaborador {apellido}, {nombre} registrado exitosamente.')
            return redirect('employees:employee_list')

    return render(request, 'employees/employee_form.html', {
        'titulo': 'Nuevo Colaborador',
        'employee_obj': None,
    })


@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        cedula = request.POST.get('cedula', '').strip()
        cargo = request.POST.get('cargo', '').strip()
        departamento = request.POST.get('departamento', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email = request.POST.get('email', '').strip()
        activo = request.POST.get('activo') == 'on'

        errors = []
        if not nombre:
            errors.append('El nombre es obligatorio.')
        if not apellido:
            errors.append('El apellido es obligatorio.')
        if not cedula:
            errors.append('La cedula es obligatoria.')
        elif Employee.objects.filter(cedula=cedula).exclude(pk=pk).exists():
            errors.append(f'La cedula "{cedula}" ya esta registrada.')
        if not cargo:
            errors.append('El cargo es obligatorio.')
        if not departamento:
            errors.append('El departamento es obligatorio.')

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            employee.nombre = nombre
            employee.apellido = apellido
            employee.cedula = cedula
            employee.cargo = cargo
            employee.departamento = departamento
            employee.telefono = telefono
            employee.email = email
            employee.activo = activo
            employee.save()
            messages.success(request, f'Colaborador {apellido}, {nombre} actualizado exitosamente.')
            return redirect('employees:employee_list')

    return render(request, 'employees/employee_form.html', {
        'titulo': 'Editar Colaborador',
        'employee_obj': employee,
    })


@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        nombre = str(employee)
        employee.delete()
        messages.success(request, f'Colaborador "{nombre}" eliminado exitosamente.')
        return redirect('employees:employee_list')

    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})


@login_required
@require_POST
def employee_create_ajax(request):
    nombre = request.POST.get('nombre', '').strip()
    if not nombre:
        return JsonResponse({'error': 'El nombre es obligatorio.'}, status=400)

    emp = Employee.objects.create(
        nombre=nombre,
        apellido=request.POST.get('apellido', '').strip(),
        cedula=request.POST.get('cedula', '').strip(),
        cargo=request.POST.get('cargo', '').strip(),
        departamento=request.POST.get('departamento', '').strip(),
        telefono=request.POST.get('telefono', '').strip(),
        email=request.POST.get('email', '').strip(),
    )
    return JsonResponse({
        'id': emp.id,
        'nombre': emp.nombre,
        'apellido': emp.apellido,
        'nombre_completo': str(emp),
        'cedula': emp.cedula,
        'cargo': emp.cargo,
        'departamento': emp.departamento,
    })
