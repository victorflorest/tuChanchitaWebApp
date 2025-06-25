from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
from decimal import Decimal
import json

from .models import (
    UserProfile, PaymentMethod, Expense, Investment, Challenge, 
    UserChallenge, TriviaQuestion, TriviaOption, TriviaRespuestaUsuario,
    PreguntaTrivia, PuntajeTrivia, RecommendationVideo
)
from .forms import (
    LoginForm, RegisterForm, ExpenseForm, PaymentMethodForm, 
    InvestmentForm, UpdateLimitForm, MonthlyLimitForm
)


class UserProfileTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(
            email='test@example.com',
            password=make_password('securepass123'),
            first_name='Gian',
            last_name='Franco',
            monthly_limit=1000.0,
            points=50,
            trivia_puntaje=200
        )

    def test_user_creation(self):
        """Test que el usuario se crea correctamente"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.monthly_limit, 1000.0)
        self.assertEqual(self.user.points, 50)
        self.assertEqual(self.user.trivia_puntaje, 200)
        self.assertEqual(str(self.user), "Gian Franco (test@example.com)")

    def test_user_unique_email(self):
        """Test que el email es único"""
        with self.assertRaises(Exception):
            UserProfile.objects.create(
                email='test@example.com',  # Email duplicado
                password='pass',
                first_name='Test',
                last_name='User'
            )

    def test_password_hashing(self):
        """Test que la contraseña se hashea correctamente"""
        self.assertTrue(check_password('securepass123', self.user.password))


class PaymentMethodTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(
            email='test2@example.com', 
            password=make_password('pass'),
            first_name='Test',
            last_name='User'
        )
        self.payment = PaymentMethod.objects.create(
            user=self.user,
            tipo=1,  # Crédito
            sistema_de_pago=2,  # Mastercard
            banco='BCP',
            ultimos_4_digitos='1234',
            mes_vencimiento=12,
            anio_vencimiento=2030
        )

    def test_payment_creation(self):
        """Test creación de método de pago"""
        self.assertEqual(self.payment.user, self.user)
        self.assertEqual(self.payment.banco, 'BCP')
        self.assertEqual(self.payment.ultimos_4_digitos, '1234')

    def test_payment_str(self):
        """Test representación string del método de pago"""
        self.assertIn('****1234', str(self.payment))
        self.assertIn('BCP', str(self.payment))

    def test_payment_choices(self):
        """Test que las opciones de tipo y sistema funcionan"""
        self.assertEqual(self.payment.get_tipo_display(), 'Crédito')
        self.assertEqual(self.payment.get_sistema_de_pago_display(), 'Mastercard')


class ExpenseTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(
            email='test3@example.com', 
            password=make_password('pass'),
            first_name='Test',
            last_name='User'
        )
        self.payment = PaymentMethod.objects.create(
            user=self.user, tipo=1, sistema_de_pago=1,
            banco='Interbank', ultimos_4_digitos='5678',
            mes_vencimiento=1, anio_vencimiento=2030
        )
        self.expense = Expense.objects.create(
            user=self.user,
            amount=250.5,
            category='Comida',
            payment_method=self.payment,
            store_name='Norkys'
        )

    def test_expense_creation(self):
        """Test creación de gasto"""
        self.assertEqual(self.expense.amount, 250.5)
        self.assertEqual(self.expense.category, 'Comida')
        self.assertEqual(self.expense.user, self.user)

    def test_expense_str(self):
        """Test representación string del gasto"""
        expected = "Comida - S/.250.5 en Norkys"
        self.assertEqual(str(self.expense), expected)

    def test_expense_categories(self):
        """Test que las categorías están disponibles"""
        categories = [choice[0] for choice in Expense.CATEGORIAS]
        self.assertIn('Comida', categories)
        self.assertIn('Educación', categories)
        self.assertIn('Ahorro', categories)


class InvestmentTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(
            email='test4@example.com', 
            password=make_password('pass'),
            first_name='Test',
            last_name='User'
        )
        self.investment = Investment.objects.create(
            user=self.user,
            company='Apple Inc.',
            symbol='AAPL',
            shares=5.0,
            price_at_purchase=150.0
        )

    def test_investment_creation(self):
        """Test creación de inversión"""
        self.assertEqual(self.investment.company, 'Apple Inc.')
        self.assertEqual(self.investment.symbol, 'AAPL')
        self.assertEqual(self.investment.shares, 5.0)

    def test_total_invested(self):
        """Test cálculo del total invertido"""
        self.assertEqual(self.investment.total_invested(), 750.0)

    @patch('requests.get')
    def test_get_current_price(self, mock_get):
        """Test obtención del precio actual"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'price': '175.50'}
        mock_get.return_value = mock_response
        
        price = self.investment.get_current_price()
        self.assertEqual(price, 175.50)

    @patch('requests.get')
    def test_current_value(self, mock_get):
        """Test cálculo del valor actual"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'price': '175.50'}
        mock_get.return_value = mock_response
        
        current_value = self.investment.current_value()
        self.assertEqual(current_value, 877.5)  # 5 * 175.50

    @patch('requests.get')
    def test_profit_loss(self, mock_get):
        """Test cálculo de ganancia/pérdida"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'price': '175.50'}
        mock_get.return_value = mock_response
        
        profit = self.investment.profit_loss()
        self.assertEqual(profit, 127.5)  # 877.5 - 750.0


class ChallengeTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(
            email='test5@example.com',
            password=make_password('pass'),
            first_name='Test',
            last_name='User',
            points=100
        )
        self.challenge_ahorro = Challenge.objects.create(
            title='Reto de Ahorro',
            description='Ahorra S/.100 en 7 días',
            type='ahorro',
            goal_amount=100.0,
            points=50,
            duration_days=7,
            condition='Ahorra mínimo S/.100'
        )
        self.challenge_no_gastos = Challenge.objects.create(
            title='No Gastar',
            description='No gastes más de S/.50 en 3 días',
            type='no_gastos',
            goal_amount=50.0,
            points=30,
            duration_days=3,
            condition='No gastar más de S/.50'
        )

    def test_challenge_creation(self):
        """Test creación de reto"""
        self.assertEqual(str(self.challenge_ahorro), 'Reto de Ahorro')
        self.assertEqual(self.challenge_ahorro.type, 'ahorro')
        self.assertEqual(self.challenge_ahorro.goal_amount, 100.0)

    def test_user_challenge_creation(self):
        """Test creación de reto de usuario"""
        user_challenge = UserChallenge.objects.create(
            user=self.user,
            challenge=self.challenge_ahorro
        )
        self.assertEqual(user_challenge.user, self.user)
        self.assertEqual(user_challenge.challenge, self.challenge_ahorro)
        self.assertFalse(user_challenge.completed)
        self.assertFalse(user_challenge.failed)

    def test_challenge_completion_ahorro(self):
        """Test completar reto de ahorro"""
        user_challenge = UserChallenge.objects.create(
            user=self.user,
            challenge=self.challenge_ahorro,
            start_date=timezone.now() - timedelta(days=1)
        )
        
        # Crear gasto de ahorro
        Expense.objects.create(
            user=self.user,
            amount=150.0,
            category='Ahorro',
            store_name='Banco',
            date=timezone.now()
        )
        
        # Simular verificación del reto
        user_challenge.check_status()
        user_challenge.refresh_from_db()
        self.user.refresh_from_db()
        
        self.assertTrue(user_challenge.completed)
        self.assertEqual(user_challenge.earned_points, 50)


class TriviaTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(
            email='test6@example.com',
            password=make_password('pass'),
            first_name='Test',
            last_name='User'
        )
        self.question = TriviaQuestion.objects.create(
            pregunta="¿Cuánto es 2+2?",
            puntos=10
        )
        self.option_correct = TriviaOption.objects.create(
            pregunta=self.question,
            texto="4",
            es_correcta=True
        )
        self.option_wrong = TriviaOption.objects.create(
            pregunta=self.question,
            texto="5",
            es_correcta=False
        )
        self.pregunta_trivia = PreguntaTrivia.objects.create(
            pregunta="¿Qué es el interés compuesto?",
            opciones={"a": "Interés simple", "b": "Interés sobre interés", "c": "Sin interés"},
            respuesta_correcta="b"
        )

    def test_trivia_question_creation(self):
        """Test creación de pregunta de trivia"""
        self.assertEqual(str(self.question), "¿Cuánto es 2+2?")
        self.assertEqual(self.question.puntos, 10)

    def test_trivia_options(self):
        """Test opciones de trivia"""
        self.assertEqual(str(self.option_correct), "4")
        self.assertTrue(self.option_correct.es_correcta)
        self.assertFalse(self.option_wrong.es_correcta)

    def test_pregunta_trivia_model(self):
        """Test modelo PreguntaTrivia"""
        self.assertEqual(str(self.pregunta_trivia), "¿Qué es el interés compuesto?")
        self.assertEqual(self.pregunta_trivia.respuesta_correcta, "b")

    def test_puntaje_trivia_creation(self):
        """Test creación de puntaje de trivia"""
        puntaje = PuntajeTrivia.objects.create(
            user=self.user,
            puntaje_total=500,
            intentos=3
        )
        self.assertEqual(puntaje.puntaje_total, 500)
        self.assertEqual(puntaje.intentos, 3)


class FormsTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(
            email='test@example.com',
            password=make_password('pass'),
            first_name='Test',
            last_name='User'
        )

    def test_login_form_valid(self):
        """Test formulario de login válido"""
        form_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_login_form_invalid(self):
        """Test formulario de login inválido"""
        form_data = {
            'email': 'invalid-email',
            'password': ''
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_register_form_valid(self):
        """Test formulario de registro válido"""
        form_data = {
            'email': 'nuevo@example.com',
            'password': 'password123',
            'first_name': 'Nuevo',
            'last_name': 'Usuario'
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_expense_form_valid(self):
        """Test formulario de gastos válido"""
        payment_method = PaymentMethod.objects.create(
            user=self.user,
            tipo=1,
            sistema_de_pago=1,
            banco='BCP',
            ultimos_4_digitos='1234',
            mes_vencimiento=12,
            anio_vencimiento=2025
        )
        
        form_data = {
            'amount': 100.50,
            'category': 'Comida',
            'payment_method': payment_method.id,
            'date': date.today(),
            'store_name': 'Restaurant'
        }
        form = ExpenseForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_payment_method_form_valid(self):
        """Test formulario de método de pago válido"""
        form_data = {
            'tipo': 1,
            'sistema_de_pago': 1,
            'banco': 'BCP',
            'ultimos_4_digitos': '5678',
            'mes_vencimiento': 12,
            'anio_vencimiento': 2025
        }
        form = PaymentMethodForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_investment_form_valid(self):
        """Test formulario de inversión válido"""
        form_data = {
            'company': 'AAPL',
            'shares': 5.5
        }
        form = InvestmentForm(data=form_data)
        self.assertTrue(form.is_valid())


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserProfile.objects.create(
            email='test@example.com',
            password=make_password('testpass123'),
            first_name='Test',
            last_name='User',
            monthly_limit=1000.0
        )

    def test_register_view_get(self):
        """Test vista de registro GET"""
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_register_view_post_valid(self):
        """Test vista de registro POST válido"""
        with patch('django.core.mail.send_mail') as mock_send_mail:
            mock_send_mail.return_value = True
            
            response = self.client.post('/register/', {
                'email': 'nuevo@example.com',
                'password': 'newpass123',
                'first_name': 'Nuevo',
                'last_name': 'Usuario'
            })
            
            # Verificar redirección al dashboard
            self.assertEqual(response.status_code, 302)
            
            # Verificar que el usuario fue creado
            user_exists = UserProfile.objects.filter(email='nuevo@example.com').exists()
            self.assertTrue(user_exists)

    def test_login_view_post_valid(self):
        """Test vista de login POST válido"""
        response = self.client.post('/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        
        # Verificar redirección al dashboard
        self.assertEqual(response.status_code, 302)
        
        # Verificar que la sesión fue creada
        self.assertIn('user_id', self.client.session)

    def test_login_view_post_invalid(self):
        """Test vista de login POST inválido"""
        response = self.client.post('/login/', {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        # No debe redirigir
        self.assertEqual(response.status_code, 200)
        
        # No debe crear sesión
        self.assertNotIn('user_id', self.client.session)

    def test_dashboard_view_authenticated(self):
        """Test vista de dashboard con usuario autenticado"""
        # Simular sesión
        session = self.client.session
        session['user_id'] = self.user.id
        session.save()
        
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.first_name)

    def test_dashboard_view_unauthenticated(self):
        """Test vista de dashboard sin autenticación"""
        response = self.client.get('/dashboard/')
        # Debe redirigir o dar error 500 (dependiendo de tu implementación)
        self.assertIn(response.status_code, [302, 500])

    def test_logout_view(self):
        """Test vista de logout"""
        # Crear sesión
        session = self.client.session
        session['user_id'] = self.user.id
        session.save()
        
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)
        
        # Verificar que la sesión fue eliminada
        self.assertNotIn('user_id', self.client.session)

    def test_profile_view(self):
        """Test vista de perfil"""
        session = self.client.session
        session['user_id'] = self.user.id
        session.save()
        
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)

    @patch('requests.get')
    def test_investment_view_with_api(self, mock_get):
        """Test vista de inversiones con API mock"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'price': '150.00'}
        mock_get.return_value = mock_response
        
        session = self.client.session
        session['user_id'] = self.user.id
        session.save()
        
        response = self.client.post('/investments/', {
            'company': 'AAPL',
            'shares': 2.5
        })
        
        # Verificar que la inversión fue creada
        investment_exists = Investment.objects.filter(user=self.user).exists()
        self.assertTrue(investment_exists)


class IntegrationTest(TestCase):
    """Tests de integración que prueban flujos completos"""
    
    def setUp(self):
        self.client = Client()
        self.user = UserProfile.objects.create(
            email='integration@example.com',
            password=make_password('testpass123'),
            first_name='Integration',
            last_name='Test',
            monthly_limit=2000.0
        )

    def test_complete_user_flow(self):
        """Test flujo completo: registro, login, agregar tarjeta, registrar gasto"""
        
        # 1. Registro de usuario
        with patch('django.core.mail.send_mail'):
            response = self.client.post('/register/', {
                'email': 'newuser@example.com',
                'password': 'newpass123',
                'first_name': 'New',
                'last_name': 'User'
            })
            self.assertEqual(response.status_code, 302)

        # 2. Login
        response = self.client.post('/login/', {
            'email': 'newuser@example.com',
            'password': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)

        # 3. Agregar método de pago
        response = self.client.post('/add_card/', {
            'tipo': 1,
            'sistema_de_pago': 1,
            'banco': 'Test Bank',
            'ultimos_4_digitos': '9999',
            'mes_vencimiento': 12,
            'anio_vencimiento': 2025
        })
        self.assertEqual(response.status_code, 302)

        # 4. Verificar que la tarjeta fue creada
        user = UserProfile.objects.get(email='newuser@example.com')
        payment_methods = PaymentMethod.objects.filter(user=user)
        self.assertEqual(payment_methods.count(), 1)

        # 5. Registrar gasto
        payment_method = payment_methods.first()
        response = self.client.post('/register_expense/', {
            'amount': 50.0,
            'category': 'Comida',
            'payment_method': payment_method.id,
            'date': date.today(),
            'store_name': 'Test Store'
        })
        self.assertEqual(response.status_code, 302)

        # 6. Verificar que el gasto fue registrado
        expenses = Expense.objects.filter(user=user)
        self.assertEqual(expenses.count(), 1)
        self.assertEqual(expenses.first().amount, 50.0)

    def test_challenge_completion_flow(self):
        """Test flujo completo de reto"""
        
        # Crear reto de ahorro
        challenge = Challenge.objects.create(
            title='Test Saving Challenge',
            description='Save S/.200 in 7 days',
            type='ahorro',
            goal_amount=200.0,
            points=100,
            duration_days=7,
            condition='Save at least S/.200'
        )

        # Usuario se une al reto
        user_challenge = UserChallenge.objects.create(
            user=self.user,
            challenge=challenge,
            start_date=timezone.now() - timedelta(days=1)
        )

        # Usuario hace gastos de ahorro
        Expense.objects.create(
            user=self.user,
            amount=250.0,
            category='Ahorro',
            store_name='Bank',
            date=timezone.now()
        )

        # Verificar estado del reto
        user_challenge.check_status()
        user_challenge.refresh_from_db()
        self.user.refresh_from_db()

        # El reto debe estar completado
        self.assertTrue(user_challenge.completed)
        self.assertEqual(user_challenge.earned_points, 100)


class UtilityTest(TestCase):
    """Tests para funciones de utilidad"""
    
    def test_password_hashing(self):
        """Test que las contraseñas se hashean correctamente"""
        password = 'testpass123'
        hashed = make_password(password)
        
        self.assertNotEqual(password, hashed)
        self.assertTrue(check_password(password, hashed))
        self.assertFalse(check_password('wrongpass', hashed))

    def test_date_calculations(self):
        """Test cálculos de fechas"""
        today = date.today()
        week_ago = today - timedelta(days=7)
        
        self.assertEqual((today - week_ago).days, 7)

    def test_money_calculations(self):
        """Test cálculos monetarios"""
        amount1 = 123.45
        amount2 = 67.89
        total = amount1 + amount2
        
        self.assertEqual(round(total, 2), 191.34)


if __name__ == '__main__':
    import unittest
    unittest.main()