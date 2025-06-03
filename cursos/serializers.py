# cursos/serializers.py
from rest_framework import serializers
from .models import Curso, Modulo, Leccion, Actividad, \
    ProgresoCurso, ProgresoModulo, ProgresoLeccion, ProgresoActividad, \
    CategoriaCurso # <-- ¡IMPORTANTE: Importa CategoriaCurso aquí!
# from django.contrib.auth.models import User # Ya no necesitas importar User directamente aquí si usas settings.AUTH_USER_MODEL en los modelos

# Serializador para CategoriaCurso
class CategoriaCursoSerializer(serializers.ModelSerializer):
    # ¡CAMBIO CLAVE AQUÍ!
    # Le decimos al serializador que el slug no es requerido en la entrada
    # y que es de solo lectura (porque el modelo lo genera).
    slug = serializers.SlugField(read_only=True, required=False)

    class Meta:
        model = CategoriaCurso
        fields = '__all__' # Esto incluirá el slug en la salida
        # O puedes especificar los campos si no quieres '__all__':
        # fields = ['id_categoria', 'nombre', 'descripcion', 'slug']

class CursoSerializer(serializers.ModelSerializer):
    # Campo de solo lectura para MOSTRAR las categorías asociadas (los nombres/detalles)
    categorias = CategoriaCursoSerializer(many=True, read_only=True)
    
    # Campo para ESCRIBIR (crear/actualizar) la relación Many-to-Many con IDs de categorías
    # ¡CAMBIO: Descomentado y ajustado para escritura!
    categoria_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CategoriaCurso.objects.all(),
        source='categorias', # Esto mapea los IDs que se envían al campo 'categorias' del modelo
        write_only=True,     # Este campo es solo para la entrada de datos, no se muestra en la salida
        required=False       # Opcional: si las categorías no son obligatorias al crear/actualizar un curso
    )

    class Meta:
        model = Curso
        # Asegúrate de incluir 'categoria_ids' aquí para que sea un campo de entrada
        fields = ['id_curso', 'nombre', 'descripcion', 'nivel', 'imagen_url', 'activo', 'categorias', 'categoria_ids']
        read_only_fields = ['id_curso'] # id_curso es un AutoField y no se debe enviar en la creación


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
        # fecha_ultimo_intento es auto_now=True en el modelo, se actualiza solo
        read_only_fields = ['fecha_inicio', 'fecha_ultimo_intento', 'fecha_completado']