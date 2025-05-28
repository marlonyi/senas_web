# usuarios/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.fields import CurrentUserDefault
from django.contrib.auth.password_validation import validate_password
from .models import PerfilUsuario, PreferenciasAccesibilidad # Asegúrate que estos modelos existan y estén correctamente definidos

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class PreferenciasAccesibilidadSerializer(serializers.ModelSerializer):
    usuario = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = PreferenciasAccesibilidad
        fields = '__all__'


# --- ¡ASEGÚRATE DE QUE ESTE SERIALIZADOR ESTÉ PRESENTE Y CORRECTAMENTE ESCRITO! ---
class PerfilUsuarioSerializer(serializers.ModelSerializer):
    # Puedes incluir el usuario relacionado aquí si quieres que se muestre en el perfil
    # Por ejemplo, para mostrar el username del usuario asociado al perfil:
    usuario = UserSerializer(read_only=True) # Muestra el objeto User completo, solo lectura
    # O si solo quieres el ID del usuario:
    # usuario_id = serializers.PrimaryKeyRelatedField(source='usuario', read_only=True)


    class Meta:
        model = PerfilUsuario
        fields = '__all__' # O lista los campos específicos que quieras exponer: ['id', 'usuario', 'puntos_experiencia', ...]
        # Puedes usar 'read_only_fields' para campos que no deben ser modificados por el cliente si no usas 'read_only=True' arriba
        read_only_fields = ['usuario'] # El usuario se asigna automáticamente, no se edita directamente a través del perfil

# Modificaciones a tu RegisterSerializer existente
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()

        PerfilUsuario.objects.create(usuario=user) # Esto ya lo tienes, genial.

        return user