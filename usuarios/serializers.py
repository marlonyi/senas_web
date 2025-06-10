# usuarios/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.fields import CurrentUserDefault
from django.contrib.auth.password_validation import validate_password

from .models import PerfilUsuario, PreferenciasAccesibilidad

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

# Serializador para PreferenciasAccesibilidad - usado para anidar
class PreferenciasAccesibilidadDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreferenciasAccesibilidad
        fields = (
            'transcripciones_activas',
            'tamano_fuente',
            'contraste_alto',
        )
        read_only_fields = ['usuario']


# Serializador para PerfilUsuario - usado para anidar en otros serializadores
class PerfilUsuarioDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = (
            'fecha_nacimiento',
            'telefono',
            'avatar',
            'biografia',
            'genero',
            'pais',
            'ciudad',
            'idioma_preferido',
            'nivel_educativo',
            'ocupacion',
        )
        read_only_fields = ('avatar',)
        
        
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True) # Para confirmar la contraseña

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': True}, # Asegurar que el email es requerido
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        # Eliminar password2 ya que no es un campo del modelo User
        validated_data.pop('password2') 

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()

        # Crear PerfilUsuario y PreferenciasAccesibilidad por defecto
        PerfilUsuario.objects.create(usuario=user)
        PreferenciasAccesibilidad.objects.create(usuario=user) # Asegúrate de que tu modelo PreferenciasAccesibilidad pueda crearse sin más datos

        return user

class MiPerfilSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username', read_only=True)
    email = serializers.EmailField(source='usuario.email', required=False)
    first_name = serializers.CharField(source='usuario.first_name', required=False)
    last_name = serializers.CharField(source='usuario.last_name', required=False)

    preferencias_accesibilidad = PreferenciasAccesibilidadDetailSerializer(
        source='usuario.preferencias_accesibilidad',
        required=False,
        allow_null=True
    )

    class Meta:
        model = PerfilUsuario
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'fecha_nacimiento',
            'telefono',
            'avatar',
            'biografia',
            'genero',
            'pais',
            'ciudad',
            'idioma_preferido',
            'nivel_educativo',
            'ocupacion',
            'preferencias_accesibilidad'
        )
        read_only_fields = ('avatar', 'username')

    def update(self, instance, validated_data):
        user = instance.usuario

        # 1. Actualizar campos del modelo User
        # Extraemos los datos del usuario.
        user_data_for_update = {}
        if 'email' in validated_data:
            user_data_for_update['email'] = validated_data.pop('email')
        if 'first_name' in validated_data:
            user_data_for_update['first_name'] = validated_data.pop('first_name')
        if 'last_name' in validated_data:
            user_data_for_update['last_name'] = validated_data.pop('last_name')

        if user_data_for_update:
            for attr, value in user_data_for_update.items():
                setattr(user, attr, value)
            user.save()

        # 2. Actualizar PreferenciasAccesibilidad (delegando al serializador anidado)
        if 'preferencias_accesibilidad' in validated_data:
            preferencias_data = validated_data.pop('preferencias_accesibilidad')

            if preferencias_obj := getattr(
                user, 'preferencias_accesibilidad', None
            ):
                # Actualizar la instancia existente de PreferenciasAccesibilidad
                # Usamos el serializador anidado para manejar la validación y actualización.
                # self.fields['preferencias_accesibilidad'] es la instancia del serializador anidado.
                # validated_data es el diccionario de datos para ese sub-serializador.
                self.fields['preferencias_accesibilidad'].update(preferencias_obj, preferencias_data)
            else:
                # Si no existe, la creamos. Esto es un fallback, ya que debería existir.
                PreferenciasAccesibilidad.objects.create(usuario=user, **preferencias_data)

        # 3. Actualizar los campos DIRECTOS del modelo PerfilUsuario
        # Excluimos explícitamente el campo 'usuario' de PerfilUsuario, ya que es una relación y se maneja por separado.
        # Creamos un diccionario con solo los campos que pertenecen directamente al PerfilUsuario.
        perfil_direct_fields = [
            'fecha_nacimiento', 'telefono', 'biografia', 'genero',
            'pais', 'ciudad', 'idioma_preferido', 'nivel_educativo', 'ocupacion'
        ]

        perfil_data_to_update = {
            k: v for k, v in validated_data.items() if k in perfil_direct_fields
        }

        for attr, value in perfil_data_to_update.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


# Serializador específico para actualizar el avatar
class AvatarUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = ('avatar',)