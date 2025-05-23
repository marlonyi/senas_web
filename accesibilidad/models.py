# accesibilidad/models.py
from django.db import models

# Este modelo podría ser para marcar qué contenido tiene qué características de accesibilidad
# class CaracteristicaContenidoAccesible(models.Model):
#     leccion = models.OneToOneField('cursos.Leccion', on_delete=models.CASCADE)
#     tiene_audio_descripcion = models.BooleanField(default=False)
#     tiene_subtitulos_lsc = models.BooleanField(default=False) # Si el video tiene subtítulos en LSC
#     def __str__(self):
#         return f"Accesibilidad para {self.leccion.titulo}"