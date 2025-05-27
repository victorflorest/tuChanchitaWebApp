from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .forms import LoginForm

from .models import (
    UserProfile, Expense, PaymentMethod, Challenge,
    UserChallenge, Investment, RecommendationVideo
)
from .forms import ExpenseForm

import json, datetime
from datetime import date, timedelta
import requests
import os
from openai import OpenAI
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# ----------------- Autenticación -----------------
def login_view(request):
    form = LoginForm(request.POST or None)
    error_message = None

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = UserProfile.objects.filter(email=email, password=password).first()
            if user:
                request.session['user_id'] = user.id
                return redirect('dashboard')
            else:
                error_message = "Credenciales inválidas"

    return render(request, 'login.html', {
        'form': form,
        'error_message': error_message
    })
    
def logout_view(request):
    request.session.flush()
    return redirect('login')


def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.points = 0
            user.monthly_limit = 0
            user.save()
            return redirect('login')
    return render(request, 'register.html', {'form': form})
# ----------------- Dashboard -----------------
def dashboard_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])
    gastos = Expense.objects.filter(user=user).order_by('-date')[:5]
    total_gastado = sum(g.amount for g in gastos)
    cards = PaymentMethod.objects.filter(user=user)

    return render(request, 'dashboard.html', {
        'user': user,
        'expenses': gastos,
        'total': total_gastado,
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

def register_view(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        email = request.POST['email']
        password = request.POST['password']
        if UserProfile.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'El correo ya está registrado.'})
        UserProfile.objects.create(
            first_name=nombre,
            email=email,
            password=password,
            monthly_limit=0,
            points=0
        )
        return redirect('login')
    return render(request, 'register.html')

def update_limit_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        nuevo_limite = float(request.POST['nuevo_limite'])
        user.monthly_limit = nuevo_limite
        user.save()
        return redirect('profile')
    return render(request, 'update_limit.html', {'user': user})

# ----------------- Gastos -----------------
def register_expense_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.user = user
            gasto.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm()
    return render(request, 'register_expense.html', {'form': form})

# ----------------- Reportes -----------------
def reports_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])
    gastos = Expense.objects.filter(user=user).order_by('-date')
    return render(request, 'reports.html', {'expenses': gastos})

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
    return render(request, 'recommendations.html', {'recomendaciones': recomendaciones})

# ----------------- ChatBot -----------------
client = OpenAI(api_key=settings.OPENAI_API_KEY)
chat_histories = {}

@csrf_exempt
def chatbot_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    user = UserProfile.objects.get(id=user_id)

    if user.id not in chat_histories:
        chat_histories[user.id] = []

    if request.method == 'POST':
        data = json.loads(request.body)
        user_input = data.get('message')

        chat_histories[user.id].append({"role": "user", "content": user_input})

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_histories[user.id]
        )

        reply = completion.choices[0].message.content
        chat_histories[user.id].append({"role": "assistant", "content": reply})
        return JsonResponse({"reply": reply})

    return render(request, 'chatbot.html', {'chat': chat_histories[user.id]})

# ----------------- Inversiones -----------------
def investment_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])
    inversiones = Investment.objects.filter(user=user)
    headers = {"Accept": "application/json"}
    api_key = settings.TWELVE_API_KEY

    for inv in inversiones:
        url = f"https://api.twelvedata.com/price?symbol={inv.symbol}&apikey={api_key}"
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            price = float(data.get('price', 0))
            inv.current_price = price
            inv.current_value = price * inv.shares
            inv.profit_loss = inv.current_value - inv.total_invested

    return render(request, 'investments.html', {'inversiones': inversiones})

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

def add_card_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        banco = request.POST.get('banco')
        ultimos_4 = request.POST.get('ultimos_4_digitos')
        mes = request.POST.get('mes_vencimiento')
        anio = request.POST.get('anio_vencimiento')

        PaymentMethod.objects.create(
            user=user,
            tipo=tipo,
            banco=banco,
            ultimos_4_digitos=ultimos_4,
            mes_vencimiento=mes,
            anio_vencimiento=anio
        )
        return redirect('profile')

    return render(request, 'add_card.html')