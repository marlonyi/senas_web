from django.apps import AppConfig


class CursosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cursos'

    def ready(self):
        import cursos.signals  # Importa tus señales aquí
        print("DEBUG: Señales de 'cursos' cargadas.") # Esto te ayudará a verificar si se cargan al iniciar el servidor