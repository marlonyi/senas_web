# gamificacion/serializers.py
from rest_framework import serializers
from .models import Logro, LogroUsuario

class LogroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logro
        fields = '__all__'

class LogroUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogroUsuario
        fields = '__all__'