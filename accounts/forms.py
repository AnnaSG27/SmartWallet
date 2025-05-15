from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import Perfil
from .models import UserProfile, Perfil, Bolsillo 

class BolsilloForm(forms.ModelForm):
    class Meta:
        model = Bolsillo
        fields = ['nombre', 'tipo', 'meta']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Vacaciones 2023'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'meta': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional',
                'step': '0.01'
            })
        }

class MovimientoForm(forms.Form):
    TIPO_MOVIMIENTO = [
        ('INGRESO', 'Ingresar dinero'),
        ('RETIRO', 'Retirar dinero'),
    ]
    
    tipo = forms.ChoiceField(
        choices=TIPO_MOVIMIENTO,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    cantidad = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        })
    )
    descripcion = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Descripción opcional'
        })
    )

class RegisterForm(UserCreationForm):
    nombres = forms.CharField(max_length=100)
    apellidos = forms.CharField(max_length=100)
    email = forms.EmailField()
    tipo_documento = forms.ChoiceField(choices=[('TI', 'Tarjeta de Identidad'), ('CC', 'Cédula de Ciudadanía')])
    documento = forms.CharField(max_length=20)

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['password1'].label = "Contraseña"
        self.fields['password2'].label = "Confirmación de contraseña"

    class Meta:
        model = User
        fields = ['username', 'nombres', 'apellidos', 'email', 'tipo_documento', 'documento', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField(label="Nombre de usuario", max_length=100)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

class PerfilForm(forms.ModelForm):
    celular = forms.CharField(max_length=15, required=False, label="Número de celular")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'perfil'):
            self.fields['celular'].initial = self.instance.perfil.celular

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if hasattr(user, 'perfil'):
                user.perfil.celular = self.cleaned_data['celular']
                user.perfil.save()
        return user

class CambiarPasswordForm(PasswordChangeForm):
    pass