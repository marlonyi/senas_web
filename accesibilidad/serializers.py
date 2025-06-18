# accesibilidad/serializers.py
from rest_framework import serializers
from .models import CaracteristicaContenidoAccesible, PreferenciaUsuarioAccesibilidad
from cursos.models import Leccion # Para el serializador de CaracteristicaContenidoAccesible
from cursos.serializers import LeccionSerializer # Para anidar la lección en la salida

class CaracteristicaContenidoAccesibleSerializer(serializers.ModelSerializer):
    leccion_titulo = serializers.CharField(source='leccion.titulo', read_only=True)
    # Si quieres ver más detalles de la lección, puedes anidar el serializador de Leccion
    # leccion_detalles = LeccionSerializer(source='leccion', read_only=True)

    class Meta:
        model = CaracteristicaContenidoAccesible
        fields = '__all__'
        read_only_fields = ['fecha_ultima_revision'] # Esto se actualiza automáticamente

class PreferenciaUsuarioAccesibilidadSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = PreferenciaUsuarioAccesibilidad
        fields = '__all__'
        read_only_fields = ['usuario'] # El usuario se asigna automáticamente