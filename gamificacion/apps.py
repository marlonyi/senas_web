# gamificacion/apps.py
from django.apps import AppConfig


class GamificacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gamificacion'
    verbose_name = 'Sistema de Gamificación' # Nombre más amigable en el admin

    def ready(self):
        import gamificacion.signals # Vamos a importar las señales aquí más adelante
        print("DEBUG: App 'gamificacion' lista.") # Mensaje de depuración