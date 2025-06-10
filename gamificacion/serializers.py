from rest_framework import serializers
from django.contrib.auth import get_user_model # ¡CAMBIO: Usar get_user_model!
from .models import PuntosUsuario, Insignia, InsigniaUsuario, Nivel # Asegúrate de importar Nivel también

User = get_user_model() # ¡NUEVO: Obtener el modelo de usuario!

class NivelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nivel
        fields = '__all__' # Incluye todos los campos del modelo Nivel

class PuntosUsuarioSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username', read_only=True)
    # --- NUEVOS CAMPOS PARA VER EL NIVEL ---
    nivel_nombre = serializers.CharField(source='nivel_actual.nombre', read_only=True)
    nivel_descripcion = serializers.CharField(source='nivel_actual.descripcion', read_only=True)

    class Meta:
        model = PuntosUsuario
        fields = ['id', 'username', 'puntos', 'fecha_ultima_actualizacion', 'nivel_nombre', 'nivel_descripcion', 'last_daily_login_award', 'login_streak']
        # Quita 'puntos' de read_only_fields si quieres modificarlo con PATCH para la prueba.
        # En un sistema real, 'puntos' se actualizaría por lógica de negocio, no directamente por la API.
        read_only_fields = ['usuario', 'fecha_ultima_actualizacion', 'nivel_nombre', 'nivel_descripcion', 'last_daily_login_award', 'login_streak']


class InsigniaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insignia
        fields = ['id', 'nombre', 'descripcion', 'imagen', 'puntos_requeridos', 'tipo_desbloqueo']

class InsigniaUsuarioSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username', read_only=True)
    insignia_nombre = serializers.CharField(source='insignia.nombre', read_only=True)
    insignia_descripcion = serializers.CharField(source='insignia.descripcion', read_only=True)
    insignia_imagen = serializers.ImageField(source='insignia.imagen', read_only=True)

    class Meta:
        model = InsigniaUsuario
        fields = ['id', 'username', 'insignia_nombre', 'insignia_descripcion', 'insignia_imagen', 'fecha_obtenida']
        read_only_fields = ['usuario', 'insignia', 'fecha_obtenida']
        
class LeaderboardUserSerializer(serializers.ModelSerializer):
    puntos_totales = serializers.IntegerField(source='puntos_gamificacion.puntos', read_only=True)
    nivel_nombre = serializers.CharField(source='puntos_gamificacion.nivel_actual.nombre', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'puntos_totales', 'nivel_nombre']