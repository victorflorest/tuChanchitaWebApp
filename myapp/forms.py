from django import forms
from .models import UserProfile
from django import forms
from .models import PaymentMethod

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['tipo', 'banco', 'ultimos_4_digitos', 'mes_vencimiento', 'anio_vencimiento']
        widgets = {
            'ultimos_4_digitos': forms.TextInput(attrs={'maxlength': 4}),
            'mes_vencimiento': forms.NumberInput(attrs={'min': 1, 'max': 12}),
            'anio_vencimiento': forms.NumberInput(attrs={'min': 2024, 'max': 2100}),
        }


class LoginForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico")
    password = forms.CharField(widget=forms.PasswordInput(), label="Contraseña")

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
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ExpenseForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['payment_method'].queryset = PaymentMethod.objects.filter(user=user)

from django import forms

class InvestmentForm(forms.Form):
    COMPANY_CHOICES = [
    ('TSLA', 'Tesla'),
    ('AAPL', 'Apple'),
    ('MSFT', 'Microsoft'),
    ('GOOGL', 'Alphabet (Google)'),
    ]

    company = forms.ChoiceField(choices=COMPANY_CHOICES)
    shares = forms.FloatField(min_value=0.01)

