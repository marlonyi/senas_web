# cursos/admin.py
from django.contrib import admin
from .models import Curso, Modulo, Leccion, Actividad, ProgresoCurso, ProgresoModulo, ProgresoLeccion, ProgresoActividad

# Registra tus modelos aquí para que aparezcan en el panel de administración
admin.site.register(Curso)
admin.site.register(Modulo)
admin.site.register(Leccion)
admin.site.register(Actividad)
admin.site.register(ProgresoCurso)
admin.site.register(ProgresoModulo)
admin.site.register(ProgresoLeccion)
admin.site.register(ProgresoActividad)