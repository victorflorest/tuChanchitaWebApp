from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/', views.profile_view, name='profile'),
    path('add-card/', views.add_card_view, name='add_card'),
    path('update-limit/', views.update_limit_view, name='update_limit'),
    path('register-expense/', views.register_expense_view, name='register_expense'),
    path('reports/', views.reports_view, name='reports'),
    path('reports/export/', views.export_pdf_view, name='export_pdf'),
    path('recomendaciones/', views.recommendations_view, name='recommendations'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('inversiones/', views.investment_view, name='investments'),
    path('retos/', views.retos_view, name='retos'),




]
