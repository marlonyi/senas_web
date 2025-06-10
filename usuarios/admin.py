# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario, PreferenciasAccesibilidad

# Define un Inline para PerfilUsuario
class PerfilUsuarioInline(admin.StackedInline): # O admin.TabularInline si prefieres una tabla
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'perfil'
    # Añade los campos que quieres que se vean en el admin aquí
    # fields = ('numero_documento', 'tipo_documento', 'fecha_nacimiento', 'pais', 'telefono', 'avatar')

# Define un Inline para PreferenciasAccesibilidad
class PreferenciasAccesibilidadInline(admin.StackedInline):
    model = PreferenciasAccesibilidad
    can_delete = False
    verbose_name_plural = 'preferencias de accesibilidad'
    # fields = ('transcripciones_activas', 'tamano_fuente', 'contraste_alto')

# Combina PerfilUsuarioInline y PreferenciasAccesibilidadInline con UserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline, PreferenciasAccesibilidadInline)

# Re-registra el modelo User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Opcional: También puedes registrar tus modelos de perfil directamente si no usas inlines
# admin.site.register(PerfilUsuario)
# admin.site.register(PreferenciasAccesibilidad)