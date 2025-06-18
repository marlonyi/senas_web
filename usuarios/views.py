# usuarios/views.py
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser # Para manejar subida de archivos
from rest_framework.views import APIView # Para vistas personalizadas de API
from rest_framework_simplejwt.tokens import RefreshToken


from django.contrib.auth.models import User
from rest_framework import permissions # <--- ASEGÚRATE DE QUE ESTA LÍNEA ESTÉ PRESENTE

from .models import PerfilUsuario, PreferenciasAccesibilidad
# Importa los serializadores actualizados/nuevos
from .serializers import (
    UserSerializer,
    PerfilUsuarioDetailSerializer,
    PreferenciasAccesibilidadDetailSerializer,
    RegisterSerializer,
    MiPerfilSerializer, # Nuevo serializador
    AvatarUpdateSerializer # Nuevo serializador
    
)

# IMPORTACIONES ADICIONALES NECESARIAS PARA ChangePasswordView
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class PerfilUsuarioViewSet(viewsets.ModelViewSet):
    queryset = PerfilUsuario.objects.all()
    serializer_class = PerfilUsuarioDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return PerfilUsuario.objects.all()
        return PerfilUsuario.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        raise permissions.PermissionDenied("La creación de perfiles se realiza automáticamente al registrar un usuario.")

    def perform_destroy(self, instance):
        raise permissions.PermissionDenied("La eliminación de perfiles no está permitida directamente. Elimine el usuario para eliminar el perfil.")


class PreferenciasAccesibilidadViewSet(viewsets.ModelViewSet):
    queryset = PreferenciasAccesibilidad.objects.all()
    serializer_class = PreferenciasAccesibilidadDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return PreferenciasAccesibilidad.objects.all()
        return PreferenciasAccesibilidad.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        if PreferenciasAccesibilidad.objects.filter(usuario=self.request.user).exists():
            raise serializers.ValidationError({"detail": "Este usuario ya tiene preferencias de accesibilidad."})
        serializer.save(usuario=self.request.user)

    def perform_destroy(self, instance):
        if instance.usuario == self.request.user:
            instance.delete()
        else:
            raise permissions.PermissionDenied("No tienes permiso para eliminar estas preferencias.")


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,) # El registro debe ser accesible sin autenticación
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Ya no necesitas crear PerfilUsuario y PreferenciasAccesibilidad aquí,
        # porque RegisterSerializer.create() ya lo hace.

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "Usuario registrado exitosamente. Se ha creado un perfil y preferencias de accesibilidad por defecto."
        }, status=status.HTTP_201_CREATED)



# Vistas para la gestión del perfil del usuario autenticado
class MiPerfilView(generics.RetrieveUpdateAPIView):
    serializer_class = MiPerfilSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        
        # Obtener o crear PerfilUsuario (si no existe, aunque el registro debería crearlo)
        perfil_usuario, created_perfil = PerfilUsuario.objects.get_or_create(usuario=user)

        # Obtener o crear PreferenciasAccesibilidad (esto es CRUCIAL para asegurar que siempre exista)
        preferencias_accesibilidad, created_prefs = PreferenciasAccesibilidad.objects.get_or_create(usuario=user)

        # Cargar el PerfilUsuario y sus relaciones para la serialización
        # Usamos 'usuario' para PerfilUsuario->User (select_related)
        # Y 'usuario__preferenciasaccesibilidad' para PerfilUsuario->User->PreferenciasAccesibilidad (prefetch_related)
        # El nombre 'preferencias_accesibilidad' es el related_name por defecto si no definiste uno
        # en PreferenciasAccesibilidad.usuario. Si definiste un related_name, úsalo aquí.
        return PerfilUsuario.objects.select_related('usuario').prefetch_related('usuario__preferencias_accesibilidad').get(usuario=user)

    def perform_update(self, serializer):
        serializer.save()


class AvatarUpdateView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        try:
            perfil_usuario = PerfilUsuario.objects.get(usuario=request.user)
        except PerfilUsuario.DoesNotExist:
            return Response({"detail": "Perfil de usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AvatarUpdateSerializer(perfil_usuario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, format=None):
        return self.put(request, format)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    class ChangePasswordSerializer(serializers.Serializer):
        old_password = serializers.CharField(required=True)
        new_password = serializers.CharField(required=True, validators=[validate_password])
        new_password2 = serializers.CharField(required=True)

        def validate(self, attrs):
            if attrs['new_password'] != attrs['new_password2']:
                raise serializers.ValidationError({"new_password": "Las nuevas contraseñas no coinciden."})
            return attrs

    def post(self, request):
        serializer = self.ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return Response({"old_password": "La contraseña antigua es incorrecta."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Contraseña actualizada exitosamente."}, status=status.HTTP_200_OK)
    
    
class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    