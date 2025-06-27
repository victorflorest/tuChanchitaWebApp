from reportlab.lib.pagesizes import letter
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
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
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User  # si usas el modelo de Django
from .forms import LoginForm
from .forms import UpdateLimitForm
from django.utils.timezone import now
from datetime import datetime
from django.shortcuts import render
from django.utils import timezone
from .models import UserProfile, UserChallenge
from .models import TriviaQuestion, TriviaOption, TriviaRespuestaUsuario
import random
from .models import PreguntaTrivia, PuntajeTrivia
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.timezone import now
from django.db.models import Sum
from django.shortcuts import render
from .models import UserProfile, Expense, PaymentMethod
from .decorators import session_login_required
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .models import Rifa
from .forms import RifaForm
from django.core.mail import send_mail
from django.urls import reverse



from .models import (
    UserProfile, Expense, PaymentMethod, Challenge,
    UserChallenge, Investment, RecommendationVideo, 
)
from .forms import ExpenseForm, PaymentMethodForm, RegisterForm, LoginForm, InvestmentForm

import json, datetime
from datetime import date, timedelta
import requests
import os
from openai import OpenAI
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .models import UserProfile
from .tokens import custom_token_generator
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
import logging

# ----------------- Autenticación -----------------

from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # Asignar todos los campos manuales que necesites
            user.password = make_password(form.cleaned_data['password'])  # Hasheamos
            user.email = form.cleaned_data['email']  # Importante
            user.save()
            request.session['user_id'] = user.id

            print("✅ Intentando enviar correo a:", user.email)
            print("Desde:", settings.DEFAULT_FROM_EMAIL)

            try:
                send_mail(
                    subject='🎉 ¡Bienvenido a TuChanchita!',
                    message=f'''
Hola {user.first_name},

¡Gracias por registrarte en TuChanchita! 🎊

Ahora puedes comenzar a llevar el control de tus gastos, asumir retos financieros y aprender jugando.

¡Disfruta la experiencia!

El equipo de TuChanchita 💰
''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                print("✅ Correo enviado correctamente")
            except Exception as e:
                print("❌ Error al enviar el correo:", e)

            return redirect('dashboard')
        else:
            print("❌ Formulario no válido:", form.errors)
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = UserProfile.objects.get(email=email)

                # Si el usuario ya está bloqueado:
                if user.is_blocked:
                    form.add_error(None, 'Este usuario ha sido bloqueado por demasiados intentos fallidos. Revisa tu correo para más información.')
                    return render(request, 'login.html', {'form': form})

                if check_password(password, user.password):
                    # LOGIN CORRECTO → resetear intentos y desbloquear por si acaso
                    user.login_attempts = 0
                    user.is_blocked = False
                    user.save()

                    request.session['user_id'] = user.id
                    return redirect('dashboard')

                else:
                    # Contraseña incorrecta → sumar intento
                    user.login_attempts += 1
                    user.save()

                    # Si llegó al intento 3:
                    if user.login_attempts >= 3:
                        user.is_blocked = True
                        user.save()

                        # Enviar email de aviso
                        send_mail(
                            subject='🚨 Alerta de seguridad en TuChanchita',
                            message=f'''
Hola {user.first_name},

Hemos detectado 4 intentos fallidos de inicio de sesión en tu cuenta.

Por seguridad, tu cuenta ha sido temporalmente bloqueada.

Si fuiste tú, te recomendamos restablecer tu contraseña.

Si no fuiste tú, contáctanos de inmediato.

Puedes recuperar el acceso usando "Olvidé mi contraseña".

El equipo de TuChanchita 💰
''',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                            fail_silently=False,
                        )

                        form.add_error(None, 'Has superado el número de intentos permitidos. Se ha enviado un correo con más información.')
                    else:
                        form.add_error(None, f'Contraseña incorrecta. Intento {user.login_attempts}/3.')

            except UserProfile.DoesNotExist:
                form.add_error('email', 'No existe un usuario con este correo electrónico.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    request.session.flush()
    return redirect('login')

# ----------------- Dashboard -----------------
@session_login_required
def dashboard_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])

    hoy = now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if hoy.month == 12:
        fin_mes = hoy.replace(year=hoy.year + 1, month=1, day=1)
    else:
        fin_mes = hoy.replace(month=hoy.month + 1, day=1)

    ultimos_gastos = Expense.objects.filter(
        user=user,
        date__range=(inicio_mes, fin_mes)
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

def upload_profile_photo(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserProfile.objects.get(id=user_id)

    if request.method == 'POST' and request.FILES.get('photo'):
        # Eliminar foto anterior si existe
        if user.photo:
            old_photo_path = os.path.join(settings.MEDIA_ROOT, user.photo.name)
            if os.path.isfile(old_photo_path):
                os.remove(old_photo_path)

        # Guardar nueva foto
        user.photo = request.FILES['photo']
        user.save()
        messages.success(request, 'Foto de perfil actualizada correctamente.')

    return redirect('profile')


# Formulario para actualizar el límite


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

    now = timezone.now()
    inicio_mes = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_mes = Expense.objects.filter(
        user=user,
        date__gte=inicio_mes,
        date__lte=now
    ).aggregate(total=Sum('amount'))['total'] or 0

    limite_mensual = getattr(user, 'monthly_limit', 0) or 0

    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=user)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.user = user
            gasto.date = timezone.now()
            
            # Calcular total con este gasto para verificar límite
            nuevo_total = total_mes + gasto.amount
            
            if nuevo_total > limite_mensual:
                # Aquí puedes enviar un mensaje o controlar en frontend (recomendado)
                # Para enviar mensaje:
                from django.contrib import messages
                messages.warning(request, '⚠️ ¡Atención! Este gasto supera tu límite mensual.')

            gasto.save()
            actualizar_retos_usuario(user)

            return redirect('dashboard')
    else:
        form = ExpenseForm(user=user)

    return render(request, 'register_expense.html', {
        'form': form,
        'total_mes': total_mes,
        'limite_mensual': limite_mensual,
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

    user = UserProfile.objects.get(id=user_id)

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
            request.session['chat_historial'] = historial

    return render(request, 'chatbot.html', {
        'historial': historial,
        'user': user,
    })


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
from datetime import timedelta, date
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from .models import UserProfile, Challenge, UserChallenge, Expense

def actualizar_retos_usuario(user):
    retos_usuario = UserChallenge.objects.filter(user=user, completed=False, failed=False)

    for uc in retos_usuario:
        reto = uc.challenge
        fecha_inicio = uc.start_date
        fecha_fin = fecha_inicio + timedelta(days=reto.duration_days)

        if reto.type == 'ahorro':
            total_ahorrado = Expense.objects.filter(
                user=user,
                category__iexact='Ahorro',
                date__range=[fecha_inicio, fecha_fin]
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            if total_ahorrado >= reto.goal_amount:
                uc.completed = True
                uc.earned_points = reto.points
                user.points += reto.points
                user.save()
                uc.save()
            elif timezone.now() > fecha_fin:
                uc.failed = True
                uc.save()

        elif reto.type == 'no_gastos':
            total_gastado = Expense.objects.filter(
                user=user,
                date__range=[fecha_inicio, fecha_fin]
            ).exclude(category__iexact='Ahorro').aggregate(Sum('amount'))['amount__sum'] or 0

            if total_gastado > reto.goal_amount:
                uc.failed = True
                uc.save()
            elif timezone.now() > fecha_fin:
                uc.completed = True
                uc.earned_points = reto.points
                user.points += reto.points
                user.save()
                uc.save()


def retos_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])
    retos_disponibles = Challenge.objects.filter(is_active=True).exclude(type='juego')
    retos_usuario = UserChallenge.objects.filter(user=user)

    retos_mostrar = []

    for uc in retos_usuario:
        reto = uc.challenge
        fecha_inicio = uc.start_date
        fecha_fin = fecha_inicio + timedelta(days=reto.duration_days)

        if uc.completed or uc.failed:
            continue

        progreso = 0
        color = '#4caf50'  # verde por defecto

        if reto.type == 'ahorro':
            total_ahorrado = Expense.objects.filter(
                user=user,
                category__iexact='Ahorro',
                date__range=[fecha_inicio, fecha_fin]
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            progreso = int(min((total_ahorrado / reto.goal_amount) * 100, 100)) if reto.goal_amount else 0
            if total_ahorrado >= reto.goal_amount:
                uc.completed = True
                uc.earned_points = reto.points
                user.points += reto.points
                user.save()
                uc.save()
                continue
            elif timezone.now() > fecha_fin:
                uc.failed = True
                uc.save()
                continue

        elif reto.type == 'no_gastos':
            total_gastos = Expense.objects.filter(
                user=user,
                date__range=[fecha_inicio, fecha_fin]
            ).exclude(category__iexact='Ahorro').aggregate(Sum('amount'))['amount__sum'] or 0

            progreso = int(min((total_gastos / reto.goal_amount) * 100, 100)) if reto.goal_amount else 0
            color = '#ef4444' if total_gastos > 0 else '#4caf50'
            if total_gastos > reto.goal_amount:
                uc.failed = True
                uc.save()
                continue
            elif timezone.now() > fecha_fin:
                uc.completed = True
                uc.earned_points = reto.points
                user.points += reto.points
                user.save()
                uc.save()
                continue

        retos_mostrar.append({
            'ur': uc,
            'progreso': progreso,
            'color': color,
        })

    if request.method == 'POST':
        reto_id = request.POST.get('reto_id')
        reto = get_object_or_404(Challenge, id=reto_id)
        if not UserChallenge.objects.filter(user=user, challenge=reto).exists():
            UserChallenge.objects.create(user=user, challenge=reto, start_date=timezone.now())
        return redirect('retos')

    top_users = UserProfile.objects.order_by('-points')[:5]

    return render(request, 'retos.html', {
        'retos': retos_disponibles.exclude(id__in=retos_usuario.values_list('challenge_id', flat=True)),
        'retos_mostrar': retos_mostrar,
        'retos_unidos': retos_usuario.values_list('challenge_id', flat=True),
        'top_users': top_users
    })

def historial_retos_view(request):
    user = UserProfile.objects.get(id=request.session['user_id'])

    historial = UserChallenge.objects.filter(
        user=user,
    ).filter(
        completed=True
    ) | UserChallenge.objects.filter(
        user=user
    ).filter(
        failed=True
    )

    historial = historial.order_by('-start_date')[:10]

    datos_historial = []
    for ur in historial:
        tipo = "Ahorro" if ur.challenge.type == "ahorro" else "No gastar"
        estado = "Completado" if ur.completed else "Fallido"
        datos_historial.append({
            'titulo': ur.challenge.title,
            'tipo': tipo,
            'estado': estado,
            'monto': ur.challenge.goal_amount,
            'puntos': ur.earned_points or 0,
            'fecha': ur.start_date.date(),
        })

    return render(request, 'historial_retos.html', {
        'datos_historial': datos_historial
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


@csrf_exempt
def trivia_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    user = UserProfile.objects.get(id=user_id)

    if 'puntos_trivia' not in request.session:
        request.session['puntos_trivia'] = 0
        request.session['fallos_trivia'] = 0
        request.session['preguntas_respondidas'] = []

    mensaje = ""
    resultado_audio = ""
    pregunta_actual = None
    opciones = {}

    if request.method == 'POST':
        seleccion = request.POST.get('opcion_seleccionada', "").strip().lower()
        pregunta_id = request.session.get('pregunta_actual_id')

        try:
            pregunta = PreguntaTrivia.objects.get(id=pregunta_id)
        except PreguntaTrivia.DoesNotExist:
            return redirect('trivia')

        if seleccion == pregunta.respuesta_correcta.strip().lower():
            request.session['puntos_trivia'] += 100
            mensaje = "✅ ¡Correcto! Has ganado 100 puntos."
            resultado_audio = "correct"
        else:
            request.session['fallos_trivia'] += 1
            mensaje = f""
            resultado_audio = "incorrect"

        if pregunta_id not in request.session['preguntas_respondidas']:
            request.session['preguntas_respondidas'].append(pregunta_id)

        if request.session['fallos_trivia'] >= 3:
            puntos_finales = request.session['puntos_trivia']
            if puntos_finales > user.trivia_puntaje:
                user.trivia_puntaje = puntos_finales
                user.save()

            puntaje, _ = PuntajeTrivia.objects.get_or_create(user=user)
            puntaje.intentos += 1
            if puntos_finales > puntaje.puntaje_total:
                puntaje.puntaje_total = puntos_finales
            puntaje.save()

            request.session['puntos_trivia'] = 0
            request.session['fallos_trivia'] = 0
            request.session['preguntas_respondidas'] = []

            return render(request, 'trivia_resultado.html', {
                'puntos': puntos_finales,
                'mensaje': mensaje,
                'resultado_audio': resultado_audio
            })

    preguntas_disponibles = PreguntaTrivia.objects.exclude(id__in=request.session['preguntas_respondidas'])
    if preguntas_disponibles.exists():
        pregunta_actual = random.choice(list(preguntas_disponibles))
        request.session['pregunta_actual_id'] = pregunta_actual.id
        opciones = pregunta_actual.opciones
    else:
        mensaje = "🎉 Has respondido todas las preguntas."
        puntos_finales = request.session['puntos_trivia']
        if puntos_finales > user.trivia_puntaje:
            user.trivia_puntaje = puntos_finales
            user.save()
        puntaje, _ = PuntajeTrivia.objects.get_or_create(user=user)
        puntaje.intentos += 1
        if puntos_finales > puntaje.puntaje_total:
            puntaje.puntaje_total = puntos_finales
        puntaje.save()

        request.session['puntos_trivia'] = 0
        request.session['fallos_trivia'] = 0
        request.session['preguntas_respondidas'] = []

        return render(request, 'trivia_resultado.html', {
            'puntos': puntos_finales,
            'mensaje': mensaje,
            'resultado_audio': "timeout"
        })

    return render(request, 'trivia.html', {
        'pregunta': pregunta_actual,
        'opciones': opciones,
        'puntos': request.session['puntos_trivia'],
        'fallos': request.session['fallos_trivia'],
        'mensaje': mensaje,
        'resultado_audio': resultado_audio
    })

def ranking_trivia_view(request):
    top_users_queryset = UserProfile.objects.order_by('-trivia_puntaje')[:3]
    top_users = list(top_users_queryset)

    # Rellenar con None si hay menos de 3
    while len(top_users) < 3:
        top_users.append(None)

    return render(request, 'trivia_ranking.html', {'top_users': top_users})

def solicitar_reset_contrasena(request):
    mensaje = ""
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = UserProfile.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = custom_token_generator.make_token(user)  # <<--- corregido aqu铆
            link = request.build_absolute_uri(f"/resetear/{uid}/{token}/")

            send_mail(
                "Recupera tu contraseña",
                f"Haz clic en el siguiente enlace para restablecer tu contraseña:\n{link}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            mensaje = "Se ha enviado un enlace a tu correo para restablecer tu contraseña."
        except UserProfile.DoesNotExist:
            mensaje = "No existe un usuario con ese correo."
    return render(request, "olvide_contrasena.html", {"mensaje": mensaje})

def resetear_contrasena(request, uidb64, token):
    mensaje = ""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserProfile.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserProfile.DoesNotExist):
        user = None

    if user is not None and custom_token_generator.check_token(user, token):
        if request.method == "POST":
            nueva_contrasena = request.POST.get("nueva_contrasena")
            confirmar_contrasena = request.POST.get("confirmar_contrasena")

            if not nueva_contrasena or not confirmar_contrasena:
                mensaje = "Debes completar ambos campos de contraseña."
            elif nueva_contrasena != confirmar_contrasena:
                mensaje = "Las contraseñas no coinciden."
            else:
                # Validación de la contraseña
                if len(nueva_contrasena) < 8:
                    mensaje = "La contraseña debe tener al menos 8 caracteres."
                elif not re.search(r'[A-Z]', nueva_contrasena):
                    mensaje = "La contraseña debe contener al menos una letra mayúscula."
                elif not re.search(r'[0-9]', nueva_contrasena):
                    mensaje = "La contraseña debe contener al menos un número."
                elif not re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|<>,./?]', nueva_contrasena):
                    mensaje = "La contraseña debe contener al menos un carácter especial."
                elif check_password(nueva_contrasena, user.password):
                    mensaje = "La nueva contraseña no puede ser igual a la anterior."
                else:
                    # Guardar la nueva contraseña Y desbloquear usuario
                    user.password = make_password(nueva_contrasena)
                    user.login_attempts = 0
                    user.is_blocked = False
                    user.save()

                    mensaje = "Contraseña restablecida correctamente. Puedes iniciar sesión."
                    return redirect("login")

        return render(request, "resetear_contrasena.html", {"validlink": True, "mensaje": mensaje})
    else:
        return render(request, "resetear_contrasena.html", {"validlink": False})
#-----------------------------------
#Eliminación de tarjeta

from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from .models import PaymentMethod, UserProfile

def delete_card(request, card_id):
    # Obtener al usuario actual desde la sesión
    user = UserProfile.objects.get(id=request.session['user_id'])
    
    # Intentamos obtener la tarjeta de pago de este usuario
    card = get_object_or_404(PaymentMethod, id=card_id, user=user)
    
    # Si encontramos la tarjeta, la eliminamos
    card.delete()

    # Redirigir al perfil
    return redirect('profile')  # Asegúrate de tener la URL correcta



@session_login_required
def crear_rifa(request):
    user = UserProfile.objects.get(id=request.session['user_id'])

    if request.method == 'POST':
        form = RifaForm(request.POST, request.FILES)
        if form.is_valid():
            rifa = form.save(commit=False)
            rifa.creado_por = user
            rifa.save()

            # ✅ Enviar correo al equipo para revisar
            admin_link = request.build_absolute_uri(
                reverse('revisar_rifa', args=[rifa.id])
            )

            send_mail(
                subject='📬 Nueva solicitud de rifa en TuChanchita',
                message=f"""
¡Hola equipo!

Un nuevo usuario ha enviado una solicitud para publicar una rifa.

📌 Título: {rifa.titulo}
👤 Usuario: {user.first_name} {user.last_name} ({user.email})
📅 Fecha del sorteo: {rifa.fecha_sorteo}

Pueden revisarla y aprobarla aquí:
{admin_link}

TuChanchita 💰
""",
                from_email=settings.DEFAULT_FROM_EMAIL,  # o settings.DEFAULT_FROM_EMAIL
                recipient_list=[settings.DEFAULT_FROM_EMAIL],  # ← cambia por tu correo real
                fail_silently=False,
            )

            return render(request, 'rifas/solicitud_enviada.html')
    else:
        form = RifaForm()
    return render(request, 'rifas/crear_rifa.html', {'form': form})

@session_login_required
def ver_rifas(request):
    user_id = request.session['user_id']

    # Buscar las rifas en las que el usuario está participando (a través de la relación con Participante)
    rifas = Rifa.objects.filter(participante__user__id=user_id).order_by('-fecha_creacion')

    # Buscar todas las rifas activas (publicadas por otros usuarios)
    otras_rifas = Rifa.objects.filter(estado='aprobado').exclude(creado_por_id=user_id).order_by('-fecha_creacion')

    return render(request, 'rifas/ver_rifas.html', {'rifas': rifas, 'otras_rifas': otras_rifas})



@staff_member_required
def revisar_rifa(request, rifa_id):
    rifa = get_object_or_404(Rifa, id=rifa_id)

    mensaje = None

    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'aprobar':
            rifa.estado = 'aprobado'
            rifa.save()
            mensaje = 'aprobada'
        elif accion == 'rechazar':
            rifa.estado = 'rechazado'
            rifa.save()
            mensaje = 'rechazada'
        else:
            mensaje = 'desconocida'

    return render(request, 'rifas/revisar_rifa.html', {'rifa': rifa, 'mensaje': mensaje})

@staff_member_required
def revisar_rifa(request, rifa_id):
    rifa = get_object_or_404(Rifa, id=rifa_id)

    mensaje = None

    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'aprobar':
            rifa.estado = 'aprobado'
            rifa.save()
            mensaje = 'aprobada'
        elif accion == 'rechazar':
            rifa.estado = 'rechazado'
            rifa.save()
            mensaje = 'rechazada'
        else:
            mensaje = 'desconocida'

        return render(request, 'rifas/confirmacion_revision.html', {
            'rifa': rifa,
            'mensaje': mensaje,
        })

    return render(request, 'rifas/revisar_rifa.html', {'rifa': rifa})


@session_login_required
def mis_rifas(request):
    user_id = request.session['user_id']
    rifas = Rifa.objects.filter(creado_por_id=user_id).order_by('-fecha_creacion')
    return render(request, 'rifas/mis_rifas.html', {'rifas': rifas})


from django.shortcuts import render, get_object_or_404, redirect
from .models import Rifa, Participante
from .forms import ParticipanteForm

def detalle_rifa(request, rifa_id):
    rifa = get_object_or_404(Rifa, id=rifa_id)
    email = request.GET.get('email', '')  # obtiene el correo de búsqueda desde el GET

    if request.method == 'POST':
        form = ParticipanteForm(request.POST, email_search=email)
        if form.is_valid():
            participante = form.save(commit=False)
            participante.rifa = rifa
            participante.save()
            return redirect('detalle_rifa', rifa_id=rifa.id)
    else:
        form = ParticipanteForm(email_search=email)  # pasa el email_search aquí

    participantes = Participante.objects.filter(rifa=rifa)

    return render(request, 'rifas/detalle_rifa.html', {
        'rifa': rifa,
        'form': form,
        'participantes': participantes,
    })


import openpyxl
from django.http import HttpResponse
from .models import Participante

def exportar_participantes_excel(request, rifa_id):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Participantes"

    encabezados = ['Nombres', 'Apellidos', 'DNI', 'Correo', 'Celular', 'Medio de Pago', 'Nro Operación', 'Fecha de Pago', 'Nro de Rifa']
    ws.append(encabezados)

    participantes = Participante.objects.filter(rifa_id=rifa_id)
    for p in participantes:
        ws.append([
            p.nombres,
            p.apellidos,
            p.dni,
            p.correo,
            p.celular,
            p.metodo_pago,
            p.numero_operacion,
            p.fecha_pago.strftime('%d/%m/%Y'),
            p.numero_rifa,
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=participantes_rifa_{rifa_id}.xlsx'
    wb.save(response)
    return response

import random
from django.contrib import messages
from django.shortcuts import redirect


def detalle_rifa_usuario(request, rifa_id):
    rifa = get_object_or_404(Rifa, id=rifa_id, estado='aprobado')  # opcional: solo rifas aprobadas
    return render(request, 'rifas/detalle_rifa_usuario.html', {'rifa': rifa})

def elegir_ganador(request, rifa_id):
    rifa = get_object_or_404(Rifa, id=rifa_id)
    
    if rifa.ganador:
        messages.error(request, f'La rifa ya tiene un ganador: {rifa.ganador.nombres} {rifa.ganador.apellidos}')
    else:
        participantes = Participante.objects.filter(rifa=rifa)
        if participantes.exists():
            ganador = random.choice(list(participantes))
            rifa.ganador = ganador
            rifa.save()

            # Mensaje para el admin
            messages.success(request, f'🎉 Ganador elegido: {ganador.nombres} {ganador.apellidos} (Rifa #{ganador.numero_rifa})')

            # Enviar correo al ganador
            if ganador.correo:
                try:
                    send_mail(
                        subject='🎉 ¡Has ganado la rifa!',
                        message=(
                            f'Hola {ganador.nombres},\n\n'
                            f'¡Felicidades! Has sido elegido como ganador de la rifa "{rifa.titulo}".\n'
                            f'Tu número ganador es: #{ganador.numero_rifa}.\n\n'
                            f'Nos pondremos en contacto contigo para coordinar la entrega del premio.\n\n'
                            f'Gracias por participar en TuChanchita.'
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[ganador.correo],
                        fail_silently=False,
                    )
                    messages.info(request, f'Se envió un correo de notificación al ganador ({ganador.correo}).')
                except Exception as e:
                    messages.warning(request, f'No se pudo enviar el correo al ganador: {e}')
            else:
                messages.warning(request, 'El ganador no tiene un correo registrado, no se pudo enviar la notificación.')
        else:
            messages.warning(request, 'No hay participantes para esta rifa.')
    
    return redirect('detalle_rifa', rifa_id=rifa.id)