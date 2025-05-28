# cursos/serializers.py
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from .models import Curso, Modulo, Leccion, Actividad, ProgresoCurso, ProgresoModulo, ProgresoLeccion, ProgresoActividad

# 1. Primero define ActividadSerializer
class ActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = '__all__'

# 2. Luego define LeccionSerializer (depende de ActividadSerializer)
class LeccionSerializer(serializers.ModelSerializer):
    actividades = ActividadSerializer(many=True, read_only=True)

    class Meta:
        model = Leccion
        fields = '__all__'

# 3. AÑADE ModuloSerializer (antes de CursoSerializer si Curso anidará Módulos, o aquí)
class ModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modulo
        fields = '__all__'

# 4. Finalmente define CursoSerializer (depende de LeccionSerializer)
class CursoSerializer(serializers.ModelSerializer):
    lecciones = LeccionSerializer(many=True, read_only=True)
    # modulos = ModuloSerializer(many=True, read_only=True) # <--- Si quieres anidar módulos en la vista de cursos

    class Meta:
        model = Curso
        fields = '__all__'

# --- AÑADE ESTOS 4 NUEVOS SERIALIZADORES DE PROGRESO AQUÍ ABAJO ---

class ProgresoCursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgresoCurso
        fields = '__all__'
        read_only_fields = ('fecha_inicio', 'fecha_completado')

class ProgresoModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgresoModulo
        fields = '__all__'
        read_only_fields = ( 'fecha_inicio', 'fecha_completado')

class ProgresoLeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgresoLeccion
        fields = '__all__'
        read_only_fields = ( 'fecha_inicio', 'fecha_completado')

class ProgresoActividadSerializer(serializers.ModelSerializer):
    # El usuario será asignado automáticamente por la vista/serializer
    usuario = serializers.HiddenField(default=CurrentUserDefault())

    # 'actividad' DEBE ser writable (no read_only) para que puedas pasarlo en el POST
    # Usamos PrimaryKeyRelatedField para esperar el ID de la actividad
    actividad = serializers.PrimaryKeyRelatedField(queryset=Actividad.objects.all())

    class Meta:
        model = ProgresoActividad
        # Incluye todos los campos que deseas exponer, incluyendo 'usuario' y 'actividad'
        fields = '__all__'
        # Si tienes un UniqueTogetherValidator en tu modelo para (usuario, actividad),
        # este serializador lo respetará.