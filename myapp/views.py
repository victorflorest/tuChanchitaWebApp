from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django import forms
from django.views.decorators.http import require_POST
from django.http import Http404
from django.db.models import Sum
from django.utils.timezone import now
from collections import defaultdict
import calendar
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from .models import UserProfile, Expense
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from datetime import date
from io import BytesIO
from .models import UserProfile, Expense
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import io
<<<<<<< Updated upstream

from .models import (
    UserProfile, Expense, PaymentMethod, Challenge,
    UserChallenge, Investment, RecommendationVideo
=======
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User  # si usas el modelo de Django
from .forms import LoginForm
from .forms import UpdateLimitForm


from .models import (
    UserProfile, Expense, PaymentMethod, Challenge,
    UserChallenge, Investment, RecommendationVideo, 
>>>>>>> Stashed changes
)
from .forms import ExpenseForm, PaymentMethodForm, RegisterForm, LoginForm, InvestmentForm

import json, datetime
from datetime import date, timedelta
import requests
import os
from openai import OpenAI
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
<<<<<<< Updated upstream

# ----------------- Autenticación -----------------
=======
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password

# ----------------- Autenticación -----------------
from django.contrib.auth.hashers import make_password

>>>>>>> Stashed changes
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
<<<<<<< Updated upstream
            user = form.save()
=======
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])  # Hash seguro
            user.save()
>>>>>>> Stashed changes
            request.session['user_id'] = user.id
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
<<<<<<< Updated upstream
            try:
                user = UserProfile.objects.get(email=email, password=password)
                request.session['user_id'] = user.id
                return redirect('dashboard')
            except UserProfile.DoesNotExist:
                form.add_error(None, 'Usuario o contraseña incorrectos')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

=======

            try:
                user = UserProfile.objects.get(email=email)

                if check_password(password, user.password):
                    request.session['user_id'] = user.id
                    return redirect('dashboard')
                else:
                    form.add_error(None, 'Contraseña incorrecta')

            except UserProfile.DoesNotExist:
                form.add_error('email', 'No existe un usuario con este correo electrónico')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


>>>>>>> Stashed changes
def logout_view(request):
    request.session.flush()
    return redirect('login')

# ----------------- Dashboard -----------------
def dashboard_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])
    ultimos_gastos = Expense.objects.filter(
        user=user,
        date__month=date.today().month,
        date__year=date.today().year
    ).order_by('-date')[:10]

    total_gastado = ultimos_gastos.aggregate(Sum('amount'))['amount__sum'] or 0
    cards = PaymentMethod.objects.filter(user=user)

    return render(request, 'dashboard.html', {
        'user': user,
        'ultimos_gastos': ultimos_gastos,
        'total_mes': total_gastado,
        'cards': cards,
        'puntos': user.points
    })

# ----------------- Perfil -----------------
def profile_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])
    cards = PaymentMethod.objects.filter(user=user)
    return render(request, 'profile.html', {
        'user': user,
        'cards': cards,
        'puntos': user.points
    })



# Formulario para actualizar el límite
<<<<<<< Updated upstream
class UpdateLimitForm(forms.Form):
    nuevo_limite = forms.FloatField(label="Nuevo límite mensual", min_value=0)
=======

>>>>>>> Stashed changes

def update_limit_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserProfile.objects.get(id=user_id)

    if request.method == 'POST':
        form = UpdateLimitForm(request.POST)
        if form.is_valid():
            nuevo_limite = form.cleaned_data['nuevo_limite']
            user.monthly_limit = nuevo_limite
            user.save()
            messages.success(request, 'Límite actualizado correctamente.')
            return redirect('profile')
    else:
        form = UpdateLimitForm(initial={'nuevo_limite': user.monthly_limit})

    return render(request, 'update_limit.html', {'form': form})


def add_card_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = user
            card.save()
            return redirect('profile')
    else:
        form = PaymentMethodForm()
    return render(request, 'add_card.html', {'form': form})

# ----------------- Gastos -----------------
def register_expense_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])
<<<<<<< Updated upstream
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.user = user
            gasto.date = timezone.now().date()  
            gasto.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm()

    tarjetas = PaymentMethod.objects.filter(user=user)
    form.fields['payment_method'].queryset = tarjetas
=======

    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=user)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.user = user
            gasto.date = timezone.now().date()
            gasto.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm(user=user)
>>>>>>> Stashed changes

    return render(request, 'register_expense.html', {
        'form': form
    })

# ----------------- Reportes -----------------
def reports_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])

    # Agrupación por categoría normalizando mayúsculas
    gastos_categoria = Expense.objects.filter(user=user).values('category').annotate(total=Sum('amount')).order_by('-total')

    # Agrupación mensual
    resumen = Expense.objects.filter(user=user).annotate(
        mes=TruncMonth('date')
    ).values('mes').annotate(total=Sum('amount')).order_by('mes')

    # Preparar resumen para el template
    resumen_mensual = [(r['mes'].strftime('%B %Y'), r['total']) for r in resumen]

    from datetime import date

    return render(request, 'reports.html', {
        'user': user,
        'gastos_categoria': gastos_categoria,
        'resumen_mensual': resumen_mensual,
        'today': date.today()
    })


def export_pdf_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])
    expenses = Expense.objects.filter(user=user)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_gastos.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    y = 750
    p.drawString(100, y, f"Reporte de gastos - {user.first_name}")
    y -= 30

    for e in expenses:
        p.drawString(100, y, f"{e.date} - {e.category} - S/. {e.amount}")
        y -= 20
        if y < 100:
            p.showPage()
            y = 750

    p.save()
    return response

# ----------------- Recomendaciones -----------------
def recommendations_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])
    recomendaciones = RecommendationVideo.objects.all()
    return render(request, 'recommendations.html', {'videos': recomendaciones})


# ----------------- ChatBot -----------------
client = OpenAI(api_key=settings.OPENAI_API_KEY)
chat_histories = {}

@csrf_exempt
def chatbot_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    # Usa sesión para almacenar historial del chat
    if 'chat_historial' not in request.session:
        request.session['chat_historial'] = []

    historial = request.session['chat_historial']

    if request.method == 'POST':
        mensaje = request.POST.get('mensaje')
        if mensaje:
            historial.append({"pregunta": mensaje})

            try:
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Eres un asistente financiero útil"},
                        *[{"role": "user", "content": h["pregunta"]} for h in historial],
                    ]
                )
                respuesta = completion.choices[0].message.content
            except Exception as e:
                respuesta = "Error al conectarse al asistente. Intenta más tarde."

            historial[-1]["respuesta"] = respuesta
            request.session['chat_historial'] = historial  # actualizar la sesión

    return render(request, 'chatbot.html', {'historial': historial})

# ----------------- Inversiones -----------------
def investment_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])
    mensaje = ""

    if request.method == 'POST':
        form = InvestmentForm(request.POST)
        if form.is_valid():
            company_symbol = form.cleaned_data['company']
            shares = form.cleaned_data['shares']

            # Obtener el precio actual desde la API
            url = f"https://api.twelvedata.com/price?symbol={company_symbol}&apikey={settings.TWELVE_API_KEY}"
            response = requests.get(url).json()
            price = float(response['price']) if 'price' in response else None

            if price is not None:
                investment = Investment.objects.create(
                    user=user,
                    company=dict(form.fields['company'].choices)[company_symbol],
                    symbol=company_symbol,
                    shares=shares,
                    price_at_purchase=price
                )
                mensaje = f"Inversión en {investment.company} registrada exitosamente."
            else:
                mensaje = "No se pudo obtener el precio actual. Intenta más tarde."
    else:
        form = InvestmentForm()

    inversiones = Investment.objects.filter(user=user)

    return render(request, 'investments.html', {
        'form': form,
        'inversiones': inversiones,
        'mensaje': mensaje
    })



@require_POST
def delete_investment_view(request, id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        inversion = Investment.objects.get(id=id, user_id=user_id)
    except Investment.DoesNotExist:
        raise Http404("La inversión no existe o no te pertenece.")

    inversion.delete()
    return redirect('investments')



# ----------------- Retos -----------------
def retos_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])
    retos_disponibles = Challenge.objects.all()
    retos_usuario = UserChallenge.objects.filter(user=user)

    for uc in retos_usuario:
        uc.check_status()

    progreso_ahorro = 0
    for uc in retos_usuario:
        if uc.challenge.type == 'ahorro' and not uc.completed:
            total_ahorrado = Expense.objects.filter(
                user=user,
                category__iexact='Ahorro',
                date__range=[uc.start_date, date.today()]
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            progreso_ahorro = total_ahorrado

    if request.method == 'POST':
        reto_id = request.POST.get('reto_id')
        reto = get_object_or_404(Challenge, id=reto_id)
        if not UserChallenge.objects.filter(user=user, challenge=reto).exists():
            UserChallenge.objects.create(user=user, challenge=reto)
        return redirect('retos')

    top_users = UserProfile.objects.order_by('-points')[:5]

    return render(request, 'retos.html', {
        'retos': retos_disponibles,
        'retos_usuario': retos_usuario,
        'retos_unidos': retos_usuario.values_list('challenge_id', flat=True),
        'progreso_ahorro': progreso_ahorro,
        'top_users': top_users
    })

def logout_view(request):
    request.session.flush()
    return redirect('login')


def export_pdf_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])
    mes_actual = date.today().strftime('%B %Y')
    fecha_emision = date.today().strftime('%B %d, %Y')

    gastos = Expense.objects.filter(
        user=user,
        date__month=date.today().month,
        date__year=date.today().year
    )

    html_string = render_to_string("estado_cuenta_pdf.html", {
        'user': user,
        'gastos': gastos,
        'mes_actual': mes_actual,
        'fecha_emision': fecha_emision,
        'total_mes': gastos.aggregate(Sum('amount'))['amount__sum'] or 0,
        'limite': user.monthly_limit,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="estado_cuenta_{user.email}.pdf"'

    pisa_status = pisa.CreatePDF(io.StringIO(html_string), dest=response)
    if pisa_status.err:
        return HttpResponse('Hubo un error generando el PDF', status=500)

    return response