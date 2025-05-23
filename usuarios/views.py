from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated # Importa IsAuthenticated
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

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = () # Permitir a cualquiera registrarse