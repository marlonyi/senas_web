from django.contrib import admin
from .models import PuntosUsuario, Insignia, InsigniaUsuario, Nivel

@admin.register(PuntosUsuario)
class PuntosUsuarioAdmin(admin.ModelAdmin):
    # ¡CAMBIO: Añadido nivel_actual, last_daily_login_award y login_streak a list_display!
    list_display = ('usuario', 'puntos', 'nivel_actual', 'last_daily_login_award', 'login_streak', 'fecha_ultima_actualizacion')
    search_fields = ('usuario__username',)
    list_filter = ('fecha_ultima_actualizacion', 'nivel_actual') # ¡CAMBIO: Añadido nivel_actual a list_filter!

@admin.register(Insignia)
class InsigniaAdmin(admin.ModelAdmin):
    # ¡CAMBIO: Añadido tipo_desbloqueo a list_display!
    list_display = ('nombre', 'puntos_requeridos', 'tipo_desbloqueo', 'imagen')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('tipo_desbloqueo',) # ¡CAMBIO: Añadido tipo_desbloqueo a list_filter!

@admin.register(InsigniaUsuario)
class InsigniaUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'insignia', 'fecha_obtenida')
    search_fields = ('usuario__username', 'insignia__nombre')
    list_filter = ('fecha_obtenida', 'insignia')

@admin.register(Nivel)
class NivelAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'puntos_minimos')
    search_fields = ('nombre',)
    list_filter = ('puntos_minimos',)