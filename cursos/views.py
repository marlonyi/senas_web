# cursos/views.py
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from .models import Curso, Modulo, Leccion, Actividad, ProgresoUsuario # <--- ¡ASEGÚRATE DE QUE Modulo ESTÉ AQUÍ!
from .serializers import CursoSerializer, ModuloSerializer, LeccionSerializer, ActividadSerializer, ProgresoUsuarioSerializer # <--- ¡ASEGÚRATE DE QUE ModuloSerializer ESTÉ AQUÍ!
from rest_framework.decorators import action
from django.utils import timezone

# Permisos: ¿Quién puede crear/editar? ¿Quién puede ver?
# Asumamos que solo los administradores o usuarios "staff" pueden crear/actualizar/eliminar cursos/lecciones/actividades.
# Todos los usuarios autenticados pueden verlos.

class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
    filter_backends = [DjangoFilterBackend] # <-- ¡AÑADE ESTA LÍNEA!
    filterset_fields = ['nivel', 'activo', 'nombre'] # <-- ¡AÑADE ESTA LÍNEA! Campos por los que quieres filtrar

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Solo los administradores (is_staff) pueden crear, actualizar o eliminar cursos
            self.permission_classes = [permissions.IsAdminUser] # O puedes crear un permiso custom
        else:
            # Todos los usuarios autenticados pueden ver los cursos
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
class ModuloViewSet(viewsets.ModelViewSet): # <--- ¡AÑADE ESTA CLASE AQUÍ!
    queryset = Modulo.objects.all() # Define qué objetos va a manejar
    serializer_class = ModuloSerializer # Asocia el serializador
    filter_backends = [DjangoFilterBackend] # <-- ¡AÑADE ESTA LÍNEA!
    filterset_fields = ['curso', 'nombre', 'orden'] # <-- ¡AÑADE ESTA LÍNEA! Puedes filtrar por ID de curso, nombre, etc.

    def get_permissions(self): # <--- ¡Añade también los permisos si son como Curso/Leccion!
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
class LeccionViewSet(viewsets.ModelViewSet):
    queryset = Leccion.objects.all()
    serializer_class = LeccionSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    # Opcional: Filtrar lecciones por curso si es necesario, aunque el anidamiento ya ayuda
    # def get_queryset(self):
    #     if 'curso_pk' in self.kwargs:
    #         return Leccion.objects.filter(curso_id=self.kwargs['curso_pk'])
    #     return Leccion.objects.all()

class ActividadViewSet(viewsets.ModelViewSet):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    # Opcional: Filtrar actividades por lección
    # def get_queryset(self):
    #     if 'leccion_pk' in self.kwargs:
    #         return Actividad.objects.filter(leccion_id=self.kwargs['leccion_pk'])
    #     return Actividad.objects.all()

class ProgresoUsuarioViewSet(viewsets.ModelViewSet):
    queryset = ProgresoUsuario.objects.all()
    serializer_class = ProgresoUsuarioSerializer
    permission_classes = [permissions.IsAuthenticated] # Solo usuarios autenticados

    def get_queryset(self):
        # Un usuario solo puede ver y gestionar su propio progreso
        return ProgresoUsuario.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        # Asegura que el progreso se asocia al usuario autenticado
        # y que la fecha de completado se establece automáticamente si no existe.
        if not serializer.validated_data.get('usuario'):
            serializer.validated_data['usuario'] = self.request.user
        if not serializer.validated_data.get('fecha_completado'):
            serializer.validated_data['fecha_completado'] = timezone.now()
        serializer.save()

    # Opcional: restringir el progreso solo para el usuario logueado en la creación
    # def create(self, request, *args, **kwargs):
    #     request.data['usuario'] = request.user.id # Forzar el usuario
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)