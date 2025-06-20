# Generated by Django 5.2.1 on 2025-05-28 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamificacion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Nivel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, unique=True)),
                ('puntos_minimos', models.IntegerField(help_text='Puntos requeridos para alcanzar este nivel', unique=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Nivel',
                'verbose_name_plural': 'Niveles',
                'ordering': ['puntos_minimos'],
            },
        ),
    ]
