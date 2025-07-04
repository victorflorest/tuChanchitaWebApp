# Generated by Django 5.2.1 on 2025-05-28 05:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_triviaquestion_triviaoption_triviarespuestausuario'),
    ]

    operations = [
        migrations.CreateModel(
            name='PreguntaTrivia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pregunta', models.CharField(max_length=255)),
                ('opciones', models.JSONField()),
                ('respuesta_correcta', models.CharField(max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='PuntajeTrivia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntaje_total', models.IntegerField(default=0)),
                ('intentos', models.IntegerField(default=0)),
                ('ultima_actualizacion', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.userprofile')),
            ],
        ),
    ]
