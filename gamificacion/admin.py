from django.contrib import admin
from .models import PuntosUsuario, Insignia, InsigniaUsuario, Nivel # <-- ¡Importa Nivel aquí!

@admin.register(PuntosUsuario)
class PuntosUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'puntos', 'fecha_ultima_actualizacion')
    search_fields = ('usuario__username',)
    list_filter = ('fecha_ultima_actualizacion',)

@admin.register(Insignia)
class InsigniaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'puntos_requeridos', 'imagen')
    search_fields = ('nombre', 'descripcion')

@admin.register(InsigniaUsuario)
class InsigniaUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'insignia', 'fecha_obtenida')
    search_fields = ('usuario__username', 'insignia__nombre')
    list_filter = ('fecha_obtenida', 'insignia')

@admin.register(Nivel) # <-- ¡Añade esta clase!
class NivelAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'puntos_minimos')
    search_fields = ('nombre',)
    list_filter = ('puntos_minimos',)