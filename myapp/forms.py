from django import forms
from .models import UserProfile
from django import forms
from .models import PaymentMethod

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['tipo', 'sistema_de_pago', 'banco', 'ultimos_4_digitos', 'mes_vencimiento', 'anio_vencimiento']
        widgets = {
            'ultimos_4_digitos': forms.TextInput(attrs={'maxlength': 4}),
            'mes_vencimiento': forms.NumberInput(attrs={'min': 1, 'max': 12}),
            'anio_vencimiento': forms.NumberInput(attrs={'min': 2024, 'max': 2100}),
        }



class LoginForm(forms.Form):
    email = forms.EmailField(label='Correo electrónico', widget=forms.EmailInput(attrs={
        'placeholder': 'Ingresa tu correo',
        'class': 'input-field'
    }))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={
        'placeholder': 'Ingresa tu contraseña',
        'class': 'input-field'
    }))


class RegisterForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email', 'password', 'first_name', 'last_name']
        widgets = {
            'password': forms.PasswordInput()
        }

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