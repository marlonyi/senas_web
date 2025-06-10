# cursos/admin.py
from django.contrib import admin
from .models import Curso, Modulo, Leccion, Actividad, \
    ProgresoCurso, ProgresoModulo, ProgresoLeccion, ProgresoActividad, \
    CategoriaCurso # <--- ¡IMPORTANTE: Añade CategoriaCurso aquí!

# Registra el nuevo modelo CategoriaCurso
@admin.register(CategoriaCurso)
class CategoriaCursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'id_categoria')
    prepopulated_fields = {'slug': ('nombre',)} # Autocompleta el slug al escribir el nombre
    search_fields = ('nombre', 'descripcion')

# Modifica el registro de Curso para incluir el campo de categorías
# Si ya tenías un admin.site.register(Curso) en la línea superior, elimínalo o comenta.
@admin.register(Curso) # Usa el decorador para registrar Curso con esta configuración
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nivel', 'activo')
    list_filter = ('nivel', 'activo', 'categorias') # Puedes filtrar por categorías
    search_fields = ('nombre', 'descripcion')
    filter_horizontal = ('categorias',) # Mejora la interfaz para ManyToMany en el admin
    # Añade aquí otros campos o inlines que ya tengas para CursoAdmin si aplica

# Registra el resto de tus modelos si no usas el decorador @admin.register para ellos
admin.site.register(Modulo)
admin.site.register(Leccion)
admin.site.register(Actividad)
admin.site.register(ProgresoCurso)
admin.site.register(ProgresoModulo)
admin.site.register(ProgresoLeccion)
admin.site.register(ProgresoActividad)