# cursos/serializers.py
from rest_framework import serializers
from .models import Curso, Modulo, Leccion, Actividad, \
    ProgresoCurso, ProgresoModulo, ProgresoLeccion, ProgresoActividad, \
    CategoriaCurso # <-- ¡IMPORTANTE: Importa CategoriaCurso aquí!
from django.contrib.auth.models import User

# Serializador para CategoriaCurso
class CategoriaCursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaCurso
        fields = '__all__' # Incluye todos los campos del modelo CategoriaCurso


class CursoSerializer(serializers.ModelSerializer):
    # Añade este campo para serializar las categorías.
    # Usamos many=True porque un curso puede tener muchas categorías.
    # read_only=True significa que este campo no se usará para crear/actualizar,
    # sino solo para mostrar la información (la relación ManyToMany se maneja por IDs).
    categorias = CategoriaCursoSerializer(many=True, read_only=True)
    # Si quisieras enviar IDs de categorías en la creación/actualización:
    # categoria_ids = serializers.PrimaryKeyRelatedField(
    #     many=True, queryset=CategoriaCurso.objects.all(), source='categorias', write_only=True
    # )

    class Meta:
        model = Curso
        fields = ['id_curso', 'nombre', 'descripcion', 'nivel', 'imagen_url', 'activo', 'categorias']
        # Si usaras categoria_ids para escribir:
        # fields = ['id_curso', 'nombre', 'descripcion', 'nivel', 'imagen_url', 'activo', 'categorias', 'categoria_ids']


class ModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modulo
        fields = '__all__'

class LeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leccion
        fields = '__all__'

class ActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = '__all__'

# --- Serializadores de Progreso ---

class ProgresoCursoSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)

    class Meta:
        model = ProgresoCurso
        fields = '__all__'
        read_only_fields = ['fecha_inicio', 'fecha_completado']

class ProgresoModuloSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    modulo_nombre = serializers.CharField(source='modulo.nombre', read_only=True)

    class Meta:
        model = ProgresoModulo
        fields = '__all__'
        read_only_fields = ['fecha_inicio', 'fecha_completado']

class ProgresoLeccionSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    leccion_titulo = serializers.CharField(source='leccion.titulo', read_only=True)

    class Meta:
        model = ProgresoLeccion
        fields = '__all__'
        read_only_fields = ['fecha_inicio', 'fecha_completado']

class ProgresoActividadSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    actividad_pregunta = serializers.CharField(source='actividad.pregunta', read_only=True)

    class Meta:
        model = ProgresoActividad
        fields = '__all__'
        read_only_fields = ['fecha_inicio', 'fecha_ultimo_intento', 'fecha_completado']