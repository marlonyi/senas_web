# usuarios/models.py
from django.db import models
from django.contrib.auth.models import User # Importamos el modelo de usuario por defecto de Django

class PerfilUsuario(models.Model):
    # Relación uno a uno con el modelo de usuario de Django
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    # Puedes añadir campos adicionales aquí si los necesitas para el perfil del usuario
    # Por ejemplo:
    # fecha_nacimiento = models.DateField(null=True, blank=True)
    # pais = models.CharField(max_length=100, blank=True)

    # Un campo para llevar la cuenta de los puntos de gamificación (opcional aquí, también puede ir en gamificacion)
    puntos_experiencia = models.IntegerField(default=0)

    def __str__(self):
        return self.usuario.username

# La tabla 'accesibilidad' en tu BD podría ser un modelo aparte o campos en PerfilUsuario
# Si 'accesibilidad' se refiere a preferencias del usuario (ej. tamaño de fuente preferido),
# podría ir aquí. Si es sobre el contenido (ej. transcripciones), irá en la app 'accesibilidad'.
# Por ahora, asumamos que son preferencias de usuario.
class PreferenciasAccesibilidad(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    transcripciones_activas = models.BooleanField(default=True)
    # Otros campos como 'tamano_fuente', 'contraste_alto', etc.
    # tamano_fuente = models.CharField(max_length=50, default='mediano')

    def __str__(self):
        return f"Preferencias de {self.usuario.username}"