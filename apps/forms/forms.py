from django import forms
from .models import Asignacion, Prestamo, Devolucion
from apps.employees.models import Employee


class AsignacionForm(forms.ModelForm):
    class Meta:
        model = Asignacion
        fields = ['tipo_equipo', 'employee', 'fecha_asignacion', 'motivo', 'observaciones']
        widgets = {
            'tipo_equipo': forms.HiddenInput(),
            'fecha_asignacion': forms.DateInput(attrs={'type': 'date', 'readonly': True}),
            'motivo': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(activo=True)
        self.fields['employee'].required = False
        self.fields['employee'].widget.attrs['style'] = 'display:none;'
        self.fields['tipo_equipo'].required = False


class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = ['employee', 'fecha_prestamo', 'fecha_prevista_devolucion', 'motivo', 'observaciones']
        widgets = {
            'fecha_prestamo': forms.DateInput(attrs={'type': 'date'}),
            'fecha_prevista_devolucion': forms.DateInput(attrs={'type': 'date'}),
            'motivo': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(activo=True)


class DevolucionForm(forms.ModelForm):
    class Meta:
        model = Devolucion
        fields = ['employee', 'asignacion', 'prestamo', 'fecha_devolucion', 'observaciones']
        widgets = {
            'fecha_devolucion': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(activo=True)
        self.fields['asignacion'].queryset = Asignacion.objects.all()
        self.fields['prestamo'].queryset = Prestamo.objects.filter(estado__in=['activo', 'vencido'])
