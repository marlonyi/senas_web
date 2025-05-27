# gamificacion/serializers.py
from rest_framework import serializers
from .models import PuntosUsuario, Insignia, InsigniaUsuario # <-- ¡Esta línea es CRUCIAL!

class PuntosUsuarioSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = PuntosUsuario
        fields = ['id', 'username', 'puntos', 'fecha_ultima_actualizacion']
        read_only_fields = ['usuario', 'puntos', 'fecha_ultima_actualizacion']

class InsigniaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insignia
        fields = ['id', 'nombre', 'descripcion', 'imagen', 'puntos_requeridos']

class InsigniaUsuarioSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username', read_only=True)
    insignia_nombre = serializers.CharField(source='insignia.nombre', read_only=True)
    insignia_descripcion = serializers.CharField(source='insignia.descripcion', read_only=True)
    insignia_imagen = serializers.ImageField(source='insignia.imagen', read_only=True)

    class Meta:
        model = InsigniaUsuario
        fields = ['id', 'username', 'insignia_nombre', 'insignia_descripcion', 'insignia_imagen', 'fecha_obtenida']
        read_only_fields = ['usuario', 'insignia', 'fecha_obtenida']