from django.contrib import admin
from django.utils.html import format_html
from .models import (
    RecommendationVideo, Challenge, UserChallenge,
    PreguntaTrivia, PuntajeTrivia, Rifa
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

@admin.register(Rifa)
class RifaAdmin(admin.ModelAdmin):
    list_display = (
        'titulo', 
        'creado_por', 
        'estado', 
        'qr_preview', 
        'selfie_preview', 
        'fecha_sorteo', 
        'fecha_creacion'
    )
    list_filter = ('estado', 'fecha_sorteo')
    search_fields = ('titulo', 'creado_por__nombres', 'dni', 'numero_celular')
    readonly_fields = ('fecha_creacion', 'qr_preview', 'foto_dni_preview', 'selfie_preview')

    fieldsets = (
        ('Información general de la rifa', {
            'fields': ('titulo', 'descripcion', 'fecha_sorteo', 'estado')
        }),
        ('Datos de contacto y verificación', {
            'fields': (
                'numero_celular', 
                'dni', 
                'qr_yape', 'qr_preview',
                'foto_dni', 'foto_dni_preview',
                'selfie_con_dni', 'selfie_preview'
            )
        }),
        ('Relación con usuario', {
            'fields': ('creado_por',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion',)
        }),
    )

    def qr_preview(self, obj):
        if obj.qr_yape:
            return format_html('<img src="{}" width="120" />', obj.qr_yape.url)
        return "-"
    qr_preview.short_description = "QR Yape"

    def foto_dni_preview(self, obj):
        if obj.foto_dni:
            return format_html('<img src="{}" width="120" />', obj.foto_dni.url)
        return "-"
    foto_dni_preview.short_description = "Foto DNI"

    def selfie_preview(self, obj):
        if obj.selfie_con_dni:
            return format_html('<img src="{}" width="120" />', obj.selfie_con_dni.url)
        return "-"
    selfie_preview.short_description = "Selfie con DNI"