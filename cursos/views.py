# cursos/views.py
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status, filters
# --- Importar los nuevos modelos de progreso ---
from .models import Curso, Modulo, Leccion, Actividad, ProgresoCurso, ProgresoModulo, ProgresoLeccion, ProgresoActividad
# --- Importar los nuevos serializadores de progreso ---
from .serializers import CursoSerializer, ModuloSerializer, LeccionSerializer, ActividadSerializer, ProgresoCursoSerializer, ProgresoModuloSerializer, ProgresoLeccionSerializer, ProgresoActividadSerializer
from rest_framework.decorators import action
from django.utils import timezone
import datetime
from django.db import IntegrityError 

# ... (Tus CursoViewSet, ModuloViewSet, LeccionViewSet (excepto el action), ActividadViewSet (excepto el action)) ...

class CursoViewSet(viewsets.ModelViewSet): # <--- Asegúrate de que esta clase exista y esté correctamente definida.
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['nombre', 'descripcion', 'nivel']
    

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()


class ModuloViewSet(viewsets.ModelViewSet): # <--- Asegúrate de que esta clase exista y esté correctamente definida.
    queryset = Modulo.objects.all()
    serializer_class = ModuloSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['curso']
    search_fields = ['nombre', 'descripcion']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

class LeccionViewSet(viewsets.ModelViewSet):
    queryset = Leccion.objects.all()
    serializer_class = LeccionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['modulo']
    search_fields = ['titulo', 'contenido_texto']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def marcar_completada(self, request, pk=None):
        leccion = self.get_object()
        usuario = request.user

        progreso_leccion, created = ProgresoLeccion.objects.get_or_create(
            usuario=usuario,
            leccion=leccion,
            defaults={
                'completado': True,
                'fecha_inicio': timezone.now(),
                'fecha_completado': timezone.now()
            }
        )

        if not created and not progreso_leccion.completado:
            progreso_leccion.completado = True
            progreso_leccion.fecha_completado = timezone.now()
            progreso_leccion.save()
        elif not created and progreso_leccion.completado:
            return Response({'detail': 'Lección ya marcada como completada.'}, status=status.HTTP_200_OK)

        serializer = ProgresoLeccionSerializer(progreso_leccion)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ActividadViewSet(viewsets.ModelViewSet):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['leccion', 'tipo_actividad']
    search_fields = ['pregunta']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enviar_actividad(self, request, pk=None):
        actividad = self.get_object()
        usuario = request.user
        respuesta_enviada = request.data.get('respuesta')

        if respuesta_enviada is None:
            return Response({"error": "Se requiere el campo 'respuesta'."}, status=status.HTTP_400_BAD_REQUEST)

        progreso_actividad, created = ProgresoActividad.objects.get_or_create(
            usuario=usuario,
            actividad=actividad,
            defaults={
                'fecha_inicio': timezone.now(),
                'intentos': 0,
                'completado': False,
                'puntuacion': 0
            }
        )

        progreso_actividad.intentos = (progreso_actividad.intentos or 0) + 1

        puntuacion_obtenida = 0
        completado = False

        # --- LÓGICA DE CALIFICACIÓN SEGÚN TIPO DE ACTIVIDAD ---
        if actividad.tipo_actividad == 'pregunta_respuesta':
            if actividad.respuesta_correcta and str(respuesta_enviada).lower() == str(actividad.respuesta_correcta).lower():
                puntuacion_obtenida = actividad.puntos
                completado = True

        elif actividad.tipo_actividad == 'seleccion_multiple':
            try:
                respuesta_usuario_idx = int(respuesta_enviada) 
                respuesta_correcta_idx = int(actividad.respuesta_correcta) 

                if actividad.opciones and \
                   0 <= respuesta_usuario_idx < len(actividad.opciones) and \
                   respuesta_usuario_idx == respuesta_correcta_idx:
                    puntuacion_obtenida = actividad.puntos
                    completado = True
            except (ValueError, TypeError):
                pass

        elif actividad.tipo_actividad == 'completar_espacios':
            if actividad.respuesta_correcta and respuesta_enviada:
                required_words = [word.strip().lower() for word in actividad.respuesta_correcta.split(',') if word.strip()]
                user_response_lower = str(respuesta_enviada).lower()

                if all(word in user_response_lower for word in required_words):
                    puntuacion_obtenida = actividad.puntos
                    completado = True

        progreso_actividad.puntuacion = puntuacion_obtenida
        progreso_actividad.completado = completado
        if completado and not progreso_actividad.fecha_completado:
            progreso_actividad.fecha_completado = timezone.now()

        progreso_actividad.save()

        serializer = ProgresoActividadSerializer(progreso_actividad)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --- NUEVOS VIEWSETS DE PROGRESO ---

class ProgresoCursoViewSet(viewsets.ModelViewSet):
    queryset = ProgresoCurso.objects.all()
    serializer_class = ProgresoCursoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return ProgresoCurso.objects.all().order_by('-fecha_inicio')
        return ProgresoCurso.objects.filter(usuario=self.request.user).order_by('-fecha_inicio')

    def perform_create(self, serializer):
        # Asigna el usuario autenticado automáticamente al crear
        if not self.request.user.is_staff:
            serializer.save(usuario=self.request.user)
        else: # Si es staff, puede crear progreso para cualquier usuario si se especifica
            usuario_id = self.request.data.get('usuario')
            if usuario_id:
                serializer.save(usuario_id=usuario_id)
            else:
                serializer.save(usuario=self.request.user) # O usa el autenticado si no se especificó otro

    def perform_update(self, serializer):
        # Asigna el usuario autenticado automáticamente al actualizar (si no es staff)
        if not self.request.user.is_staff and serializer.instance.usuario != self.request.user:
            raise permissions.PermissionDenied("No tienes permiso para actualizar el progreso de otro usuario.")
        serializer.save()

class ProgresoModuloViewSet(viewsets.ModelViewSet):
    queryset = ProgresoModulo.objects.all()
    serializer_class = ProgresoModuloSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return ProgresoModulo.objects.all().order_by('-fecha_inicio')
        return ProgresoModulo.objects.filter(usuario=self.request.user).order_by('-fecha_inicio')

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            serializer.save(usuario=self.request.user)
        else:
            usuario_id = self.request.data.get('usuario')
            if usuario_id:
                serializer.save(usuario_id=usuario_id)
            else:
                serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        if not self.request.user.is_staff and serializer.instance.usuario != self.request.user:
            raise permissions.PermissionDenied("No tienes permiso para actualizar el progreso de otro usuario.")
        serializer.save()
class ProgresoLeccionViewSet(viewsets.ModelViewSet):
    queryset = ProgresoLeccion.objects.all()
    serializer_class = ProgresoLeccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return ProgresoLeccion.objects.all().order_by('-fecha_inicio')
        return ProgresoLeccion.objects.filter(usuario=self.request.user).order_by('-fecha_inicio')

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            serializer.save(usuario=self.request.user)
        else:
            usuario_id = self.request.data.get('usuario')
            if usuario_id:
                serializer.save(usuario_id=usuario_id)
            else:
                serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        if not self.request.user.is_staff and serializer.instance.usuario != self.request.user:
            raise permissions.PermissionDenied("No tienes permiso para actualizar el progreso de otro usuario.")
        serializer.save()

class ProgresoActividadViewSet(viewsets.ModelViewSet):
    queryset = ProgresoActividad.objects.all()
    serializer_class = ProgresoActividadSerializer
    #permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return ProgresoActividad.objects.all().order_by('-fecha_inicio')
        return ProgresoActividad.objects.filter(usuario=self.request.user).order_by('-fecha_inicio')

    def perform_create(self, serializer):
        # Lógica para crear el progreso:
        # Si el usuario no es staff, el usuario se asigna automáticamente al usuario autenticado.
        if not self.request.user.is_staff:
            serializer.save(usuario=self.request.user)
        else:
            # Si es staff, puede crear progreso para cualquier usuario si se especifica 'usuario' en el body.
            # Si no se especifica 'usuario', se usa el usuario staff autenticado.
            usuario_id = self.request.data.get('usuario')
            if usuario_id:
                serializer.save(usuario_id=usuario_id) # Usar usuario_id para evitar cargar el objeto completo
            else:
                serializer.save(usuario=self.request.user)


    def perform_update(self, serializer):
        # Lógica para actualizar el progreso:
        # Un usuario normal solo puede actualizar su propio progreso.
        if not self.request.user.is_staff and serializer.instance.usuario != self.request.user:
            raise permissions.PermissionDenied("No tienes permiso para actualizar el progreso de otro usuario.")
        serializer.save()