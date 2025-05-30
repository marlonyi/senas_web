# gamificacion/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save # <--- ¡IMPORTANTE! Añadir esto
from django.dispatch import receiver         # <--- ¡IMPORTANTE! Añadir esto
from django.utils import timezone
import logging # <--- ¡IMPORTANTE! Añadir esto para los logs en la señal

logger = logging.getLogger(__name__) # <--- ¡IMPORTANTE! Inicializar el logger aquí

class Nivel(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    puntos_minimos = models.IntegerField(unique=True, help_text='Puntos requeridos para alcanzar este nivel')
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['puntos_minimos']
        verbose_name = 'Nivel'
        verbose_name_plural = 'Niveles'

    def __str__(self):
        return f'Nivel {self.nombre} ({self.puntos_minimos}+ puntos)'


class PuntosUsuario(models.Model):
    usuario = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='puntos_gamificacion'
    )
    puntos = models.IntegerField(default=0)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    last_daily_reward_date = models.DateField(null=True, blank=True)

    nivel_actual = models.ForeignKey(
        'Nivel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios_en_nivel',
        # Si tienes problemas con migraciones y usuarios existentes,
        # puedes añadir un default temporalmente así:
        # default=1 # Asumiendo que tu nivel 'Novato' tiene ID 1
    )

    class Meta:
        verbose_name = 'Puntos de Usuario'
        verbose_name_plural = 'Puntos de Usuarios'

    def __str__(self):
        return f'Puntos de {self.usuario.username}: {self.puntos}'

    # <--- ¡IMPORTANTE! Añadir este método al modelo PuntosUsuario
    def _update_nivel_actual(self):
        """
        Actualiza el nivel del usuario basado en sus puntos.
        """
        # Filtramos por puntos_minimos <= puntos del usuario y ordenamos de forma descendente
        # para obtener el nivel con los puntos_minimos más altos pero que el usuario aún cumple.
        nuevo_nivel = Nivel.objects.filter(puntos_minimos__lte=self.puntos).order_by('-puntos_minimos').first()

        if nuevo_nivel and self.nivel_actual != nuevo_nivel:
            self.nivel_actual = nuevo_nivel
            # La señal post_save se encargará de guardar si el nivel cambia.


class Insignia(models.Model):
    TIPO_PUNTOS = 'puntos'
    TIPO_ACCION = 'accion'
    TIPO_COMPLEJIDAD = 'complejidad'

    TIPOS_DESBLOQUEO = [
        (TIPO_PUNTOS, 'Por Puntos Totales'),
        (TIPO_ACCION, 'Por Acción Específica'),
        (TIPO_COMPLEJIDAD, 'Por Criterio Complejo'),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='insignias/', blank=True, null=True)
    puntos_requeridos = models.IntegerField(
        default=0,
        help_text='Puntos necesarios para obtener esta insignia (solo si "Por Puntos Totales")',
    )
    tipo_desbloqueo = models.CharField(
        max_length=50,
        choices=TIPOS_DESBLOQUEO,
        default=TIPO_ACCION,
        help_text='Define cómo se desbloquea esta insignia',
    )

    class Meta:
        verbose_name = 'Insignia'
        verbose_name_plural = 'Insignias'

    def __str__(self):
        return self.nombre


class InsigniaUsuario(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='insignias_obtenidas'
    )
    insignia = models.ForeignKey(
        Insignia, on_delete=models.CASCADE, related_name='usuarios_con_insignia'
    )
    fecha_obtenida = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Insignia de Usuario'
        verbose_name_plural = 'Insignias de Usuarios'
        unique_together = (
            'usuario',
            'insignia',
        )

    def __str__(self):
        return f"{self.usuario.username} obtuvo '{self.insignia.nombre}'"


# <--- ¡IMPORTANTE! Añadir esta señal al final del archivo
@receiver(post_save, sender=PuntosUsuario)
def update_user_level(sender, instance, created, **kwargs):
    # Solo actualizar el nivel si la instancia no es nueva O si el nivel ya está establecido.
    # Evitar recursión si la instancia es nueva y el nivel se establece por primera vez.
    old_level = instance.nivel_actual
    instance._update_nivel_actual() # Esto calcula el nuevo nivel y lo asigna a instance.nivel_actual

    # Si el nivel cambió, guardar la instancia para persistir el nuevo nivel.
    if instance.nivel_actual != old_level:
        # Desactivar la señal temporalmente para evitar un bucle de guardado.
        post_save.disconnect(update_user_level, sender=PuntosUsuario)
        instance.save(update_fields=['nivel_actual'])
        post_save.connect(update_user_level, sender=PuntosUsuario)
        logger.debug(f"DEBUG: Nivel de {instance.usuario.username} actualizado a {instance.nivel_actual.nombre}")

# Tu serializer está bien, no lo incluyo aquí para no repetir.
# class LeaderboardUserSerializer(serializers.ModelSerializer):
#     # ...