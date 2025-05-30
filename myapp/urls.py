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
    path('logout/', views.logout_view, name='logout'),
    path('eliminar-inversion/<int:id>/', views.delete_investment_view, name='delete_investment'),
    path('historial-retos/', views.historial_retos_view, name='historial_retos'),
    path('trivia/', views.trivia_view, name='trivia'),
    path('trivia-ranking/', views.ranking_trivia_view, name='trivia_ranking'),
    path('upload-profile-photo/', views.upload_profile_photo, name='upload_profile_photo'),
    path("olvide-contrasena/", views.solicitar_reset_contrasena, name="olvide_contrasena"),
    path("resetear/<uidb64>/<token>/", views.resetear_contrasena, name="resetear_contrasena"),
    path('delete_card/<int:card_id>/', views.delete_card, name='delete_card'),
]
