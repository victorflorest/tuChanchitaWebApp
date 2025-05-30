from django.contrib import admin
from .models import (
    RecommendationVideo, Challenge, UserChallenge,
    PreguntaTrivia, PuntajeTrivia
)

@admin.register(PreguntaTrivia)
class PreguntaTriviaAdmin(admin.ModelAdmin):
    list_display = ('pregunta', 'mostrar_opciones', 'respuesta_correcta')
    search_fields = ('pregunta',)

    def mostrar_opciones(self, obj):
        return ", ".join([f"{k}: {v}" for k, v in obj.opciones.items()])

@admin.register(PuntajeTrivia)
class PuntajeTriviaAdmin(admin.ModelAdmin):
    list_display = ('user', 'puntaje_total', 'intentos', 'ultima_actualizacion')
    search_fields = ('user__email',)

    def save_model(self, request, obj, form, change):
        # Guardar el objeto normalmente
        super().save_model(request, obj, form, change)

        # También actualizar el puntaje en UserProfile si es mayor
        if obj.puntaje_total > obj.user.trivia_puntaje:
            obj.user.trivia_puntaje = obj.puntaje_total
            obj.user.save()

admin.site.register(RecommendationVideo)
admin.site.register(Challenge)
admin.site.register(UserChallenge)
