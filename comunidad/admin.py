# comunidad/admin.py
from django.contrib import admin
from .models import Foro, Comentario, MeGustaComentario

@admin.register(Foro)
class ForoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'creador', 'fecha_creacion', 'activo')
    list_filter = ('activo', 'fecha_creacion', 'creador')
    search_fields = ('titulo', 'descripcion')
    raw_id_fields = ('creador',) # Para manejar la selección de usuario de forma eficiente en el admin

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('autor', 'foro', 'contenido_preview', 'fecha_creacion', 'parent_comentario')
    list_filter = ('fecha_creacion', 'autor', 'foro')
    search_fields = ('contenido',)
    raw_id_fields = ('autor', 'foro', 'parent_comentario')

    def contenido_preview(self, obj):
        return f"{obj.contenido[:50]}..." if len(obj.contenido) > 50 else obj.contenido
    contenido_preview.short_description = "Contenido (Preview)"

@admin.register(MeGustaComentario)
class MeGustaComentarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'comentario', 'fecha_creacion')
    list_filter = ('fecha_creacion', 'usuario', 'comentario')
    raw_id_fields = ('usuario', 'comentario')