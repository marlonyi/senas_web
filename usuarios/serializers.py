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


# RegisterSerializer (sin cambios, ya funciona)
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    perfil = PerfilUsuarioDetailSerializer(required=False)
    preferencias_accesibilidad = PreferenciasAccesibilidadDetailSerializer(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name', 'perfil', 'preferencias_accesibilidad')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        perfil_data = validated_data.pop('perfil', {})
        preferencias_data = validated_data.pop('preferencias_accesibilidad', {})
        validated_data.pop('password2')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()

        PerfilUsuario.objects.create(usuario=user, **perfil_data)
        PreferenciasAccesibilidad.objects.create(usuario=user, **preferencias_data)

        return user


# Serializador para ver y editar el perfil del usuario autenticado (MiPerfilView)
class MiPerfilSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username', read_only=True)
    email = serializers.EmailField(source='usuario.email', required=False)
    first_name = serializers.CharField(source='usuario.first_name', required=False)
    last_name = serializers.CharField(source='usuario.last_name', required=False)

    # El nombre del campo anidado en el serializador es 'preferencias_accesibilidad'.
    # El 'source' indica de dónde viene el dato para la serialización de salida.
    # required=False permite que no se envíe en la entrada.
    # read_only=False (por defecto) o no especificarlo, permite que los datos se pasen al update.
    # Si lo pones en read_only=True, NO podrás actualizarlo a través de este serializador.
    preferencias_accesibilidad = PreferenciasAccesibilidadDetailSerializer(
        source='usuario.preferencias_accesibilidad',
        required=False
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
            'preferencias_accesibilidad' # Asegúrate de que esté aquí para la salida
        )
        read_only_fields = ('avatar',) # El avatar lo gestionaremos con una vista de actualización de imagen separada

    def update(self, instance, validated_data):
        # 1. Extraer los datos que corresponden a los modelos relacionados (User y PreferenciasAccesibilidad)
        user = instance.usuario

        # Extraer los campos del User. Pop los elimina de validated_data.
        email_data = validated_data.pop('email', None)
        first_name_data = validated_data.pop('first_name', None)
        last_name_data = validated_data.pop('last_name', None)

        # Extraer los datos de las preferencias de accesibilidad. Pop los elimina de validated_data.
        # La clave es 'preferencias_accesibilidad' porque así es como se define el campo en este serializador.
        preferencias_data = validated_data.pop('preferencias_accesibilidad', None)

        # 2. Actualizar campos del modelo User
        if email_data is not None:
            user.email = email_data
        if first_name_data is not None:
            user.first_name = first_name_data
        if last_name_data is not None:
            user.last_name = last_name_data
        user.save()

        # 3. Actualizar o crear PreferenciasAccesibilidad
        if preferencias_data is not None:
            PreferenciasAccesibilidad.objects.update_or_create(
                usuario=user,
                defaults=preferencias_data
            )

        # 4. Actualizar los campos directos del modelo PerfilUsuario
        # Después de los .pop(), 'validated_data' solo debería contener campos directos de PerfilUsuario.
        # Para ser aún más seguro, filtramos explícitamente por los nombres de los campos de PerfilUsuario.
        # Esto previene errores si alguna clave inesperada quedara en validated_data.
        perfil_fields = [f.name for f in PerfilUsuario._meta.get_fields() if f.concrete and not f.is_relation]
        perfil_data_to_update = {k: v for k, v in validated_data.items() if k in perfil_fields}

        for attr, value in perfil_data_to_update.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


# Serializador específico para actualizar el avatar
class AvatarUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = ('avatar',)