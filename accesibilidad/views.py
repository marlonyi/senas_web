# accesibilidad/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import CaracteristicaContenidoAccesible, PreferenciaUsuarioAccesibilidad
from .serializers import CaracteristicaContenidoAccesibleSerializer, PreferenciaUsuarioAccesibilidadSerializer
from cursos.models import Leccion # Para CaracteristicaContenidoAccesible

class CaracteristicaContenidoAccesibleViewSet(viewsets.ModelViewSet):
    queryset = CaracteristicaContenidoAccesible.objects.all()
    serializer_class = CaracteristicaContenidoAccesibleSerializer
    # Solo los administradores pueden gestionar las características de accesibilidad del contenido
    permission_classes = [permissions.IsAdminUser] 
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['leccion', 'tiene_audio_descripcion', 'tiene_subtitulos_lsc', 'tiene_transcripcion_texto', 'es_compatible_lector_pantalla']
    search_fields = ['leccion__titulo', 'leccion__contenido_texto']

    # Sobrescribir perform_create para asegurar que solo haya una CaracteristicaContenidoAccesible por Leccion
    def perform_create(self, serializer):
        leccion_id = self.request.data.get('leccion')
        if CaracteristicaContenidoAccesible.objects.filter(leccion_id=leccion_id).exists():
            return Response(
                {"detail": "Ya existe una característica de accesibilidad para esta lección."},
                status=status.HTTP_409_CONFLICT
            )
        serializer.save()

class PreferenciaUsuarioAccesibilidadViewSet(viewsets.ModelViewSet):
    queryset = PreferenciaUsuarioAccesibilidad.objects.all()
    serializer_class = PreferenciaUsuarioAccesibilidadSerializer
    # Los usuarios autenticados pueden ver y gestionar sus propias preferencias
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Si es un administrador, puede ver todas las preferencias
        if self.request.user.is_staff:
            return PreferenciaUsuarioAccesibilidad.objects.all()
        # Si no es administrador, solo puede ver sus propias preferencias
        return PreferenciaUsuarioAccesibilidad.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        # Asegurarse de que el usuario solo pueda crear una preferencia para sí mismo
        if PreferenciaUsuarioAccesibilidad.objects.filter(usuario=self.request.user).exists():
            return Response(
                {"detail": "Ya tienes una configuración de preferencias de accesibilidad. Por favor, actualízala en su lugar."},
                status=status.HTTP_409_CONFLICT
            )
        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        # Asegurarse de que el usuario solo pueda actualizar sus propias preferencias
        if not self.request.user.is_staff and serializer.instance.usuario != self.request.user:
            raise permissions.PermissionDenied("No tienes permiso para actualizar las preferencias de otro usuario.")
        serializer.save()

    def perform_destroy(self, instance):
        # Asegurarse de que el usuario solo pueda eliminar sus propias preferencias
        if not self.request.user.is_staff and instance.usuario != self.request.user:
            raise permissions.PermissionDenied("No tienes permiso para eliminar las preferencias de otro usuario.")
        instance.delete()

    @action(detail=False, methods=['get', 'patch'], permission_classes=[permissions.IsAuthenticated], url_path='mi-preferencia')
    def my_preferences(self, request):
        """
        Permite a un usuario autenticado obtener o actualizar sus propias preferencias de accesibilidad.
        """
        try:
            preferencia = PreferenciaUsuarioAccesibilidad.objects.get(usuario=request.user)
        except PreferenciaUsuarioAccesibilidad.DoesNotExist:
            # Si no existe, puedes optar por crear una por defecto o devolver un 404
            if request.method == 'GET':
                return Response({"detail": "No se encontraron preferencias de accesibilidad para este usuario."}, status=status.HTTP_404_NOT_FOUND)
            elif request.method == 'PATCH':
                # Si se intenta actualizar sin que exista, se puede crear una nueva
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(usuario=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'GET':
            serializer = self.get_serializer(preferencia)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = self.get_serializer(preferencia, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)