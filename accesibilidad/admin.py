# accesibilidad/admin.py
from django.contrib import admin
from .models import CaracteristicaContenidoAccesible, PreferenciaUsuarioAccesibilidad

@admin.register(CaracteristicaContenidoAccesible)
class CaracteristicaContenidoAccesibleAdmin(admin.ModelAdmin):
    list_display = ('leccion', 'tiene_audio_descripcion', 'tiene_subtitulos_lsc', 'tiene_transcripcion_texto', 'es_compatible_lector_pantalla', 'fecha_ultima_revision')
    list_filter = ('tiene_audio_descripcion', 'tiene_subtitulos_lsc', 'tiene_transcripcion_texto', 'es_compatible_lector_pantalla')
    search_fields = ('leccion__titulo',)
    raw_id_fields = ('leccion',) # Para facilitar la selección de lección si hay muchas

@admin.register(PreferenciaUsuarioAccesibilidad)
class PreferenciaUsuarioAccesibilidadAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'preferencia_lsc', 'preferencia_audio_descripcion', 'preferencia_transcripcion_texto', 'tamano_fuente', 'contraste_alto', 'habilitar_reconocimiento_senas', 'idioma_senas_preferido')
    list_filter = ('preferencia_lsc', 'preferencia_audio_descripcion', 'preferencia_transcripcion_texto', 'tamano_fuente', 'contraste_alto', 'habilitar_reconocimiento_senas', 'idioma_senas_preferido')
    search_fields = ('usuario__username',)
    raw_id_fields = ('usuario',) # Para facilitar la selección de usuario