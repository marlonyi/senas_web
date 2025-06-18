# accesibilidad/models.py
from django.db import models
from django.conf import settings # Para referenciar el modelo de usuario
from cursos.models import Leccion # Para enlazar con las lecciones

class CaracteristicaContenidoAccesible(models.Model):
    """
    Define las características de accesibilidad de un contenido específico,
    como una lección.
    """
    leccion = models.OneToOneField(
        Leccion, 
        on_delete=models.CASCADE, 
        related_name='caracteristicas_accesibilidad',
        help_text="Lección a la que se aplican estas características de accesibilidad."
    )
    tiene_audio_descripcion = models.BooleanField(
        default=False, 
        help_text="Indica si el contenido tiene una descripción de audio para personas con discapacidad visual."
    )
    tiene_subtitulos_lsc = models.BooleanField(
        default=False, 
        help_text="Indica si el video o contenido tiene subtítulos en Lengua de Señas Colombiana."
    )
    tiene_transcripcion_texto = models.BooleanField(
        default=False, 
        help_text="Indica si el contenido tiene una transcripción de texto completa."
    )
    es_compatible_lector_pantalla = models.BooleanField(
        default=False, 
        help_text="Indica si el contenido está optimizado para lectores de pantalla."
    )
    fecha_ultima_revision = models.DateTimeField(
        auto_now=True, 
        help_text="Fecha de la última revisión de las características de accesibilidad."
    )

    class Meta:
        verbose_name = "Característica de Contenido Accesible"
        verbose_name_plural = "Características de Contenido Accesible"
        ordering = ['leccion__titulo'] # Ordenar por el título de la lección

    def __str__(self):
        return f"Accesibilidad para: {self.leccion.titulo}"


class PreferenciaUsuarioAccesibilidad(models.Model):
    """
    Permite a cada usuario configurar sus preferencias de accesibilidad.
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='preferencias_accesibilidad',
        help_text="Usuario al que pertenecen estas preferencias de accesibilidad."
    )
    preferencia_lsc = models.BooleanField(
        default=False, 
        help_text="El usuario prefiere contenido con Lengua de Señas Colombiana."
    )
    preferencia_audio_descripcion = models.BooleanField(
        default=False, 
        help_text="El usuario prefiere contenido con descripciones de audio."
    )
    preferencia_transcripcion_texto = models.BooleanField(
        default=False, 
        help_text="El usuario prefiere contenido con transcripciones de texto."
    )
    # Opciones de tamaño de fuente
    TAMANO_FUENTE_CHOICES = [
        ('pequeno', 'Pequeño'),
        ('normal', 'Normal'),
        ('grande', 'Grande'),
        ('extragrande', 'Extra Grande'),
    ]
    tamano_fuente = models.CharField(
        max_length=20, 
        choices=TAMANO_FUENTE_CHOICES, 
        default='normal',
        help_text="Tamaño de fuente preferido por el usuario."
    )
    contraste_alto = models.BooleanField(
        default=False, 
        help_text="El usuario prefiere un esquema de colores de alto contraste."
    )
    # ¡NUEVO CAMPO para la visión de IA!
    habilitar_reconocimiento_senas = models.BooleanField(
        default=False,
        help_text="El usuario desea usar el reconocimiento de señas a través de la cámara para actividades o traducciones."
    )
    # ¡NUEVO CAMPO para idiomas de señas!
    IDIOMA_SENAS_CHOICES = [
        ('LSC', 'Lengua de Señas Colombiana'),
        ('ASL', 'American Sign Language'),
        ('LSE', 'Lengua de Signos Española'),
        # Agrega más si es necesario
    ]
    idioma_senas_preferido = models.CharField(
        max_length=10,
        choices=IDIOMA_SENAS_CHOICES,
        default='LSC',
        help_text="Idioma de señas preferido por el usuario."
    )
    
    class Meta:
        verbose_name = "Preferencia de Usuario de Accesibilidad"
        verbose_name_plural = "Preferencias de Usuario de Accesibilidad"

    def __str__(self):
        return f"Preferencias de {self.usuario.username}"