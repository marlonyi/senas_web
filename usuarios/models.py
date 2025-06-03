# usuarios/models.py
from django.db import models
from django.conf import settings # ¡CAMBIO: Importar settings aquí!

class PerfilUsuario(models.Model):
    # ¡CAMBIO: Usar settings.AUTH_USER_MODEL!
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mi_perfil')

    # Campos esenciales / muy recomendados para el perfil (los que ya tenías)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatares/', blank=True, null=True)
    biografia = models.TextField(blank=True, null=True)

    # Campos adicionales sugeridos ahora
    genero = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        choices=[
            ('masculino', 'Masculino'),
            ('femenino', 'Femenino'),
            ('otro', 'Otro'),
            ('no_decir', 'Prefiero no decir')
        ]
    )
    pais = models.CharField(max_length=100, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    idioma_preferido = models.CharField(
        max_length=7,
        default='es-co', # O el idioma por defecto que consideres
        choices=[
            ('es-co', 'Español (Colombia)'),
            ('en', 'English'),
            ('es', 'Español (General)'), # Si planeas soportar español genérico también
            # Añade más idiomas si los necesitas
        ]
    )
    nivel_educativo = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('primaria', 'Primaria'),
            ('secundaria', 'Secundaria'),
            ('tecnico', 'Técnico'),
            ('universitario', 'Universitario'),
            ('posgrado', 'Posgrado'),
            ('otro', 'Otro')
        ]
    )
    ocupacion = models.CharField(max_length=100, blank=True, null=True) # O TextField si quieres más detalle

    def __str__(self):
        return self.usuario.username

# El modelo PreferenciasAccesibilidad ya lo tienes y está bien
# Solo asegúrate de que los campos 'tamano_fuente' y 'contraste_alto' estén definidos allí.
class PreferenciasAccesibilidad(models.Model):
    # ¡CAMBIO: Usar settings.AUTH_USER_MODEL y añadir related_name único!
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='preferencias_accesibilidad_usuario_app' # ¡CAMBIO CRÍTICO AQUÍ!
    )
    transcripciones_activas = models.BooleanField(default=True)
    tamano_fuente = models.CharField(
        max_length=50,
        default='mediano',
        choices=[
            ('pequeño', 'Pequeño'),
            ('mediano', 'Mediano'),
            ('grande', 'Grande'),
        ]
    )
    contraste_alto = models.BooleanField(default=False)

    def __str__(self):
        return f"Preferencias de {self.usuario.username}"