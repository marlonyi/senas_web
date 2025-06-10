# cursos/apps.py
from django.apps import AppConfig


class CursosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cursos'

    def ready(self):
        # Importar tus señales aquí para que se registren cuando la aplicación esté lista
        import cursos.signals # <--- ¡Esta línea ya debería estar ahí!
        print("DEBUG: Señales de 'cursos' cargadas.") # Esto te ayudará a verificar si se cargan al iniciar el servidor