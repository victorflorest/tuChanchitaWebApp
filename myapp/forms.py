from django import forms
from .models import UserProfile
from django import forms
from .models import PaymentMethod
from .models import Participante
import re
import requests
from .models import Rifa

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['tipo', 'sistema_de_pago', 'banco', 'ultimos_4_digitos', 'mes_vencimiento', 'anio_vencimiento']
        widgets = {
            'ultimos_4_digitos': forms.TextInput(attrs={'maxlength': 4, 'placeholder': 'Ej: 1234'}),
            'mes_vencimiento': forms.NumberInput(attrs={'min': 1, 'max': 12}),
            'anio_vencimiento': forms.NumberInput(attrs={'min': 2024, 'max': 2100}),
        }

    def clean_ultimos_4_digitos(self):
        ultimos_4 = self.cleaned_data.get('ultimos_4_digitos')

        if not ultimos_4 or not ultimos_4.isdigit():
            raise forms.ValidationError('Solo se permiten números en este campo.')

        if len(ultimos_4) != 4:
            raise forms.ValidationError('Debe ingresar exactamente 4 dígitos.')

        return ultimos_4

    def clean_mes_vencimiento(self):
        mes = self.cleaned_data.get('mes_vencimiento')

        if mes is None:
            raise forms.ValidationError('Este campo es obligatorio.')

        if not (1 <= mes <= 12):
            raise forms.ValidationError('El mes debe estar entre 1 y 12.')

        return mes

    def clean_anio_vencimiento(self):
        from datetime import date
        anio = self.cleaned_data.get('anio_vencimiento')

        if anio is None:
            raise forms.ValidationError('Este campo es obligatorio.')

        current_year = date.today().year
        if anio < current_year:
            raise forms.ValidationError('El año no puede ser menor al actual.')

        return anio

    def clean(self):
        cleaned_data = super().clean()
        mes = cleaned_data.get('mes_vencimiento')
        anio = cleaned_data.get('anio_vencimiento')

        # Validar que la fecha completa no sea una tarjeta ya vencida
        from datetime import date
        if mes and anio:
            today = date.today()
            tarjeta_fecha = date(year=anio, month=mes, day=1)
            tarjeta_fecha = tarjeta_fecha.replace(day=28)  # poner fin de mes

            if tarjeta_fecha < today.replace(day=1):
                raise forms.ValidationError('La tarjeta no puede estar vencida.')




# forms.py
from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(label='Correo electrónico', widget=forms.EmailInput(attrs={
        'placeholder': 'Ingresa tu correo',
        'class': 'input-field'
    }))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={
        'placeholder': 'Ingresa tu contraseña',
        'class': 'input-field'
    }))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        # Ejemplo: validar que ambos campos estén completos
        if not email:
            self.add_error('email', 'Por favor ingresa tu correo electrónico.')
        if not password:
            self.add_error('password', 'Por favor ingresa tu contraseña.')
        
        # Aquí podrías agregar más validaciones personalizadas si quieres (por ejemplo: verificar si el email existe en la BD)



class RegisterForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email', 'password', 'first_name', 'last_name']
        widgets = {
            'password': forms.PasswordInput(attrs={
                'placeholder': 'Contraseña (mín. 8, mayúscula, número, caracter especial)',
                'class': 'input-field'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Correo electrónico',
                'class': 'input-field'
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Nombre',
                'class': 'input-field'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Apellido',
                'class': 'input-field'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # 1️⃣ Validar que no esté en la BD
        if UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado. Intenta iniciar sesión o recupera tu contraseña.')

        # 2️⃣ Validar con Abstract API (correo real)
        API_KEY = '83e60704ad924a309ec603243337b8c5'  # REEMPLAZA con tu API KEY
        url = f"https://emailvalidation.abstractapi.com/v1/?api_key={API_KEY}&email={email}"

        try:
            response = requests.get(url)
            result = response.json()

            # Validar formato válido
            if not result.get('is_valid_format', {}).get('value', False):
                raise forms.ValidationError('El correo no tiene un formato válido.')

            # Validar que no sea temporal
            if result.get('is_disposable_email', {}).get('value', False):
                raise forms.ValidationError('No se permiten correos temporales o desechables.')

            # Validar que acepte correos
            if result.get('deliverability') != 'DELIVERABLE':
                raise forms.ValidationError('No se pudo verificar que este correo acepte emails.')

        except Exception as e:
            print(f"Error validando email con API: {e}")
            raise forms.ValidationError('Hubo un problema al verificar el correo. Intenta nuevamente.')

        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if len(password) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('La contraseña debe contener al menos una letra mayúscula.')
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError('La contraseña debe contener al menos un número.')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|<>,./?]', password):
            raise forms.ValidationError('La contraseña debe contener al menos un caracter especial.')

        return password

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$', first_name):
            raise forms.ValidationError('El nombre solo puede contener letras y espacios.')

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$', last_name):
            raise forms.ValidationError('El apellido solo puede contener letras y espacios.')

        return last_name

    def clean(self):
        cleaned_data = super().clean()
        required_fields = ['email', 'password', 'first_name', 'last_name']

        for field in required_fields:
            value = cleaned_data.get(field)
            if not value:
                self.add_error(field, 'Este campo es obligatorio.')

class MonthlyLimitForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['monthly_limit']


from .models import Expense, PaymentMethod
from django import forms

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'category', 'payment_method', 'date', 'store_name']
        widgets = {
            'amount': forms.NumberInput(attrs={'placeholder': 'S/. 0.00', 'class': 'input-field'}),
            'category': forms.Select(attrs={'class': 'input-field'}),
            'payment_method': forms.Select(attrs={'class': 'input-field'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'input-field'}),
            'store_name': forms.TextInput(attrs={'placeholder': 'Tienda o servicio', 'class': 'input-field'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['payment_method'].queryset = PaymentMethod.objects.filter(user=user)



class InvestmentForm(forms.Form):
    COMPANY_CHOICES = [
    ('TSLA', 'Tesla'),
    ('AAPL', 'Apple'),
    ('MSFT', 'Microsoft'),
    ('GOOGL', 'Alphabet (Google)'),
    ]

    company = forms.ChoiceField(choices=COMPANY_CHOICES)
    shares = forms.FloatField(min_value=0.01)

class UpdateLimitForm(forms.Form):
    nuevo_limite = forms.FloatField(label='Nuevo límite mensual', min_value=0)

class RifaForm(forms.ModelForm):
    class Meta:
        model = Rifa
        fields = [
            'titulo', 'descripcion', 'fecha_sorteo','foto_premio',
            'qr_yape', 'dni', 'numero_celular',
            'foto_dni', 'selfie_con_dni'
        ]
        widgets = {
            'fecha_sorteo': forms.DateInput(attrs={'type': 'date'}),
        }



class ParticipanteForm(forms.ModelForm):
    class Meta:
        model = Participante
        fields = ['nombres', 'apellidos', 'correo', 'dni', 'celular', 'numero_operacion', 'metodo_pago', 'fecha_pago', 'user']

    user = forms.ModelChoiceField(
        queryset=UserProfile.objects.none(),  # Inicialmente no muestra nada
        required=True,
        label="Seleccionar Usuario",
        empty_label="Buscar por Correo",
        widget=forms.Select(attrs={'class': 'input-field'})
    )

    def __init__(self, *args, **kwargs):
        email_search = kwargs.pop('email_search', '')  # Buscar por correo si se pasa un email
        super().__init__(*args, **kwargs)
        
        # Si hay un email de búsqueda, filtramos los usuarios por correo
        if email_search:
            self.fields['user'].queryset = UserProfile.objects.filter(email__icontains=email_search)
        else:
            self.fields['user'].queryset = UserProfile.objects.all()  # Si no, mostrar todos