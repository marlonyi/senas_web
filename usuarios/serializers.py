# usuarios/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PerfilUsuario, PreferenciasAccesibilidad

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name'] # Campos que quieres exponer del usuario de Django

class PerfilUsuarioSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True) # Para mostrar los datos del usuario relacionado

    class Meta:
        model = PerfilUsuario
        fields = '__all__' # Todos los campos del PerfilUsuario
        # O puedes especificar los campos que quieres:
        # fields = ['id', 'usuario', 'puntos_experiencia']

class PreferenciasAccesibilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreferenciasAccesibilidad
        fields = '__all__'
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()

        # Crea también un PerfilUsuario para el nuevo usuario
        PerfilUsuario.objects.create(usuario=user)

        return user