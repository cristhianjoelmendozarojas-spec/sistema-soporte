from django import forms
from .models import Asignacion, AsignacionDetalle, Prestamo, PrestamoDetalle, Devolucion, DevolucionDetalle
from apps.employees.models import Employee
from apps.equipment.models import Equipment


class AsignacionForm(forms.ModelForm):
    class Meta:
        model = Asignacion
        fields = ['codigo', 'employee', 'fecha_asignacion', 'motivo', 'observaciones']
        widgets = {
            'fecha_asignacion': forms.DateInput(attrs={'type': 'date'}),
            'motivo': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(activo=True)


class AsignacionDetalleForm(forms.ModelForm):
    class Meta:
        model = AsignacionDetalle
        fields = ['equipment', 'estado_entrega', 'observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipment'].queryset = Equipment.objects.filter(estado='disponible')


class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = ['codigo', 'employee', 'fecha_prestamo', 'fecha_prevista_devolucion', 'motivo', 'observaciones']
        widgets = {
            'fecha_prestamo': forms.DateInput(attrs={'type': 'date'}),
            'fecha_prevista_devolucion': forms.DateInput(attrs={'type': 'date'}),
            'motivo': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(activo=True)


class PrestamoDetalleForm(forms.ModelForm):
    class Meta:
        model = PrestamoDetalle
        fields = ['equipment', 'estado_entrega']
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipment'].queryset = Equipment.objects.filter(estado='disponible')


class DevolucionForm(forms.ModelForm):
    class Meta:
        model = Devolucion
        fields = ['codigo', 'employee', 'asignacion', 'prestamo', 'fecha_devolucion', 'observaciones']
        widgets = {
            'fecha_devolucion': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(activo=True)
        self.fields['asignacion'].queryset = Asignacion.objects.all()
        self.fields['prestamo'].queryset = Prestamo.objects.filter(estado__in=['activo', 'vencido'])


class DevolucionDetalleForm(forms.ModelForm):
    class Meta:
        model = DevolucionDetalle
        fields = ['equipment', 'estado_recibido', 'observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }
