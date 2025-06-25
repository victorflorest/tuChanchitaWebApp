from django.db import models
import requests
from django.conf import settings
from datetime import date, timedelta
from django.db.models import Sum
from django.utils import timezone
from datetime import date
from django.utils.timezone import now
from datetime import timedelta


class UserProfile(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    monthly_limit = models.FloatField(default=0.0)
    points = models.IntegerField(default=0)
    trivia_puntaje = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    login_attempts = models.IntegerField(default=0)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class PaymentMethod(models.Model):
    TIPO_CHOICES = [
        (1, 'Crédito'),
        (2, 'Débito'),
    ]

    TIPO_SISTEMAPAGO = [
        (1, 'Visa'),
        (2, 'Mastercard',)
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    tipo = models.IntegerField(choices=TIPO_CHOICES, default=1)
    sistema_de_pago = models.IntegerField(choices=TIPO_SISTEMAPAGO, default=1)
    banco = models.CharField(max_length=100)
    ultimos_4_digitos = models.CharField(max_length=4)
    mes_vencimiento = models.IntegerField()
    anio_vencimiento = models.IntegerField()

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.banco} ****{self.ultimos_4_digitos}"



class Expense(models.Model):
    CATEGORIAS = [
        ('Comida', 'Comida'),
        ('Educación', 'Educación'),
        ('Ropa', 'Ropa'),
        ('Otros', 'Otros'),
        ('Ahorro', 'Ahorro')
    ]

    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    amount = models.FloatField()
    category = models.CharField(max_length=50, choices=CATEGORIAS)
    payment_method = models.ForeignKey('PaymentMethod', on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(default=timezone.now)  # actualizado a DateTimeField
    store_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.category} - S/.{self.amount} en {self.store_name}"


class RecommendationVideo(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    url_video = models.URLField()  # enlace de YouTube u otro
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Investment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    company = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    shares = models.FloatField()
    price_at_purchase = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def total_invested(self):
        return round(self.shares * self.price_at_purchase, 2)

    def get_current_price(self):
        url = f"https://api.twelvedata.com/price?symbol={self.symbol}&apikey={settings.TWELVE_API_KEY}"
        response = requests.get(url).json()
        return float(response['price']) if 'price' in response else None

    def current_value(self):
        current_price = self.get_current_price()
        if current_price:
            return round(self.shares * current_price, 2)
        return None

    def profit_loss(self):
        current = self.current_value()
        if current:
            return round(current - self.total_invested(), 2)
        return None

    def __str__(self):
        return f"{self.company} - {self.shares} acciones"



class Challenge(models.Model):
    CHALLENGE_TYPES = [
    ('no_gastos', 'No gastar'),
    ('ahorro', 'Ahorro'),
    ]
    goal_amount = models.FloatField(null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=CHALLENGE_TYPES, default='no_gastar')
    points = models.IntegerField()
    duration_days = models.IntegerField()
    condition = models.CharField(max_length=200)  # lógica de validación (luego se puede extender)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class UserChallenge(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    completed = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    earned_points = models.IntegerField(default=0)

    def check_status(self):
        if self.completed:
            return

        deadline = self.start_date + timedelta(days=self.challenge.duration_days)

        if timezone.now() > deadline:
            return  # Ya expiró

        gastos = Expense.objects.filter(user=self.user, date__range=[self.start_date, deadline])

        if self.challenge.type == 'ahorro':
            total_ahorro = sum(g.amount for g in gastos if g.category.lower() == 'ahorro')
            self.progress = total_ahorro
            if self.challenge.goal_amount and total_ahorro >= self.challenge.goal_amount:
                self.completed = True
                self.earned_points = self.challenge.points
                self.user.points += self.challenge.points
                self.user.save()
                self.save()



class TriviaQuestion(models.Model):
    pregunta = models.TextField()
    puntos = models.IntegerField(default=10)

    def __str__(self):
        return self.pregunta

class TriviaOption(models.Model):
    pregunta = models.ForeignKey(TriviaQuestion, related_name='opciones', on_delete=models.CASCADE)
    texto = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False)

    def __str__(self):
        return self.texto

class TriviaRespuestaUsuario(models.Model):
    usuario = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(TriviaQuestion, on_delete=models.CASCADE)
    respondida_correctamente = models.BooleanField()
    fecha = models.DateTimeField(auto_now_add=True)


class PreguntaTrivia(models.Model):
    pregunta = models.CharField(max_length=255)
    opciones = models.JSONField()  # ej. {"a": "Opción A", "b": "Opción B", "c": "Opción C"}
    respuesta_correcta = models.CharField(max_length=1)  # "a", "b", "c", etc.

    def __str__(self):
        return self.pregunta

class PuntajeTrivia(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    puntaje_total = models.IntegerField(default=0)
    intentos = models.IntegerField(default=0)  # intentos fallidos actuales
    ultima_actualizacion = models.DateTimeField(auto_now=True)
