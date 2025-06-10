# gamificacion/models.py
from django.db import models
from django.conf import settings # ¡CAMBIO: Usar settings para AUTH_USER_MODEL!
from django.utils import timezone

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
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='puntos_gamificacion' # ¡CAMBIO AQUÍ!
    )
    puntos = models.IntegerField(default=0)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    # Renombramos a 'last_daily_login_award' para mayor claridad y coherencia con el signals.py
    # ¡IMPORTANTE! Asegúrate de que este nombre sea 'last_daily_login_award'
    last_daily_login_award = models.DateField(null=True, blank=True)
    login_streak = models.IntegerField(default=0)

    nivel_actual = models.ForeignKey(
        'Nivel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios_en_nivel',
    )

    class Meta:
        verbose_name = 'Puntos de Usuario'
        verbose_name_plural = 'Puntos de Usuarios'

    def __str__(self):
        return f'Puntos de {self.usuario.username}: {self.puntos}'

    # Mantenemos este método, pero será llamado desde signals.py
    def update_nivel_based_on_points(self): # Renombrado para mayor claridad
        """
        Actualiza el nivel del usuario basado en sus puntos.
        Retorna True si el nivel cambió, False en caso contrario.
        """
        nuevo_nivel = Nivel.objects.filter(puntos_minimos__lte=self.puntos).order_by('-puntos_minimos').first()
        if nuevo_nivel and self.nivel_actual != nuevo_nivel:
            self.nivel_actual = nuevo_nivel
            # NO GUARDES AQUÍ. La señal post_save en signals.py lo hará.
            return True
        return False


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
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='insignias_obtenidas' # ¡CAMBIO AQUÍ!
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