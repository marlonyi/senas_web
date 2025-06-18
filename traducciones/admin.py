# traducciones/admin.py
from django.contrib import admin
from .models import CategoriaSenda, Senda

@admin.register(CategoriaSenda)
class CategoriaSendaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_creacion', 'activo')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')

@admin.register(Senda)
class SendaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'fecha_creacion', 'activo')
    list_filter = ('activo', 'categoria', 'fecha_creacion')
    search_fields = ('titulo', 'contenido')
    raw_id_fields = ('categoria',) # Para facilitar la selección de categoría si hay muchas