# gamificacion/models.py
from django.db import models
from django.contrib.auth.models import User
from rest_framework import serializers
from django.utils import timezone # Para fechas con zona horaria

class PuntosUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='puntos_gamificacion')
    puntos = models.IntegerField(default=0)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    # --- NUEVO CAMPO ---
    nivel_actual = models.ForeignKey('Nivel', on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios_en_nivel')

    class Meta:
        verbose_name = "Puntos de Usuario"
        verbose_name_plural = "Puntos de Usuarios"

    def __str__(self):
        return f"Puntos de {self.usuario.username}: {self.puntos}"

class Insignia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='insignias/', blank=True, null=True) # Requiere Pillow instalado
    puntos_requeridos = models.IntegerField(default=0, help_text="Puntos necesarios para obtener esta insignia (si aplica)")
    # Puedes añadir otros campos para el criterio de la insignia, ej:
    # tipo_desbloqueo = models.CharField(max_length=50, choices=TIPOS_DESBLOQUEO)

    class Meta:
        verbose_name = "Insignia"
        verbose_name_plural = "Insignias"

    def __str__(self):
        return self.nombre

class InsigniaUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='insignias_obtenidas')
    insignia = models.ForeignKey(Insignia, on_delete=models.CASCADE, related_name='usuarios_con_insignia')
    fecha_obtenida = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Insignia de Usuario"
        verbose_name_plural = "Insignias de Usuarios"
        unique_together = ('usuario', 'insignia') # Un usuario solo puede tener una instancia de una insignia

    def __str__(self):
        return f"{self.usuario.username} obtuvo '{self.insignia.nombre}'"

class Nivel(models.Model):
    nombre = models.CharField(max_length=50, unique=True) # Nombre único del nivel (ej. "Novato", "Veterano")
    puntos_minimos = models.IntegerField(unique=True, help_text="Puntos requeridos para alcanzar este nivel")
    descripcion = models.TextField(blank=True, null=True)
    # Podrías añadir una imagen para el nivel también:
    # imagen = models.ImageField(upload_to='niveles/', blank=True, null=True)

    class Meta:
        ordering = ['puntos_minimos'] # Los niveles se ordenan por los puntos requeridos
        verbose_name = "Nivel"
        verbose_name_plural = "Niveles"

    def __str__(self):
        return f"Nivel {self.nombre} ({self.puntos_minimos}+ puntos)"

class LeaderboardUserSerializer(serializers.ModelSerializer):
    # Esto accederá al related_name 'puntos_gamificacion' de PuntosUsuario
    puntos_totales = serializers.IntegerField(source='puntos_gamificacion.puntos', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'puntos_totales']
