from rest_framework import viewsets, generics, status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import permissions
from django.contrib.auth.models import User
from .models import PerfilUsuario, PreferenciasAccesibilidad
from .serializers import UserSerializer, PerfilUsuarioSerializer, PreferenciasAccesibilidadSerializer, RegisterSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class PerfilUsuarioViewSet(viewsets.ModelViewSet):
    queryset = PerfilUsuario.objects.all()
    serializer_class = PerfilUsuarioSerializer
    permission_classes = [IsAuthenticated] # Solo usuarios autenticados

    def get_queryset(self):
        # Un usuario solo puede ver y editar su propio perfil
        return PerfilUsuario.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        # No permitimos crear perfiles directamente, se crean con el registro
        # Si alguien intenta hacer un POST aquí, se manejará por la lógica del serializer de registro
        pass # O puedes lanzar una excepción si quieres ser más estricto

    def perform_update(self, serializer):
        # Asegura que el perfil que se actualiza pertenece al usuario logueado
        if serializer.instance.usuario == self.request.user:
            serializer.save()
        else:
            raise permissions.PermissionDenied("No tienes permiso para editar este perfil.")

    def perform_destroy(self, instance):
        # Generalmente, no se elimina un perfil sin eliminar el usuario.
        # Puedes deshabilitar esta acción si no es necesaria.
        raise permissions.PermissionDenied("No se permite eliminar perfiles directamente.")


class PreferenciasAccesibilidadViewSet(viewsets.ModelViewSet):
    queryset = PreferenciasAccesibilidad.objects.all()
    serializer_class = PreferenciasAccesibilidadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PreferenciasAccesibilidad.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        # Primero, verifica si el usuario ya tiene preferencias para evitar duplicados
        if PreferenciasAccesibilidad.objects.filter(usuario=self.request.user).exists():
            # Si ya existen, levanta un error 400 Bad Request
            raise serializers.ValidationError({"detail": "Este usuario ya tiene preferencias de accesibilidad."})

        # Asigna el usuario actual a la instancia antes de guardarla
        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.usuario == self.request.user:
            serializer.save()
        else:
            from rest_framework import permissions # Importa permissions aquí
            raise permissions.PermissionDenied("No tienes permiso para editar estas preferencias.")

    def perform_destroy(self, instance):
        if instance.usuario == self.request.user:
            instance.delete()
        else:
            from rest_framework import permissions # Importa permissions aquí
            raise permissions.PermissionDenied("No tienes permiso para eliminar estas preferencias.")

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    # Usar AllowAny explícitamente es más claro que ()
    permission_classes = (AllowAny,)

    # <--- ¡AÑADE ESTE MÉTODO 'post' A TU CLASE RegisterView! --->
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) # Si no es válido, lanza un 400 Bad Request
        user = serializer.save() # Llama al método create de tu serializador

        # Estructura de respuesta personalizada que deseas
        return Response({
            "message": "Usuario registrado exitosamente.",
            "user": {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }, status=status.HTTP_201_CREATED)