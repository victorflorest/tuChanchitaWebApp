# Generated by Django 5.2.1 on 2025-05-26 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_challenge_userchallenge'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='type',
            field=models.CharField(choices=[('no_gastos', 'No gastar'), ('ahorro', 'Ahorrar monto'), ('juego', 'Juego')], default='ahorro', max_length=20),
        ),
    ]
