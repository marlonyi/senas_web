# cursos/views.py
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status, filters
from rest_framework import serializers # Importado explícitamente para serializers.ValidationError

# Importa CategoriaCurso aquí
from .models import Curso, Modulo, Leccion, Actividad, ProgresoCurso, ProgresoModulo, ProgresoLeccion, ProgresoActividad, CategoriaCurso
# Importa CategoriaCursoSerializer
from .serializers import CursoSerializer, ModuloSerializer, LeccionSerializer, ActividadSerializer, \
    ProgresoCursoSerializer, ProgresoModuloSerializer, ProgresoLeccionSerializer, ProgresoActividadSerializer, \
    CategoriaCursoSerializer # <--- ¡IMPORTANTE: Importa CategoriaCursoSerializer aquí!

from rest_framework.decorators import action
from django.utils import timezone 
import datetime 
from django.db import IntegrityError 


# --- NUEVO: ViewSet para CategoriaCurso ---
class CategoriaCursoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaCurso.objects.all().order_by('nombre')
    serializer_class = CategoriaCursoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # ¡OPCIONAL: Puedes cambiarlo según tu decisión, pero lo dejo como estaba!


class CursoViewSet(viewsets.ModelViewSet):
    # Modificamos el queryset para que el filtro por categorías sea más eficiente
    queryset = Curso.objects.all().prefetch_related('categorias')
    serializer_class = CursoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['nombre', 'descripcion', 'nivel']
    
    # Añadimos 'categorias' a los campos de filtro
    filterset_fields = ['nivel', 'activo', 'categorias'] # Filtra por ID de categoría
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()


class ModuloViewSet(viewsets.ModelViewSet):
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
                'fecha_completado': timezone.now() # Esto se establece aquí si se crea por primera vez
            }
        )

        if not created:
            if progreso_leccion.completado:
                return Response({'detail': 'Lección ya marcada como completada.'}, status=status.HTTP_200_OK)

            progreso_leccion.completado = True
            progreso_leccion.fecha_completado = timezone.now() # Y también si se actualiza a completada
            progreso_leccion.save()
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
        # sourcery skip: use-contextlib-suppress
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
            if actividad.respuesta_correcta and respuesta_enviada is not None:
                # Normalizar ambas respuestas para comparación
                respuesta_correcta_norm = str(actividad.respuesta_correcta).strip().lower()
                respuesta_enviada_norm = str(respuesta_enviada).strip().lower()
                if respuesta_enviada_norm == respuesta_correcta_norm:
                    puntuacion_obtenida = actividad.puntos
                    completado = True

        elif actividad.tipo_actividad == 'seleccion_multiple':
            try:
                # Asegurarse de que respuesta_enviada sea una cadena antes de int()
                # y normalizar para evitar errores de espacios en blanco
                respuesta_usuario_idx = int(str(respuesta_enviada).strip())
                respuesta_correcta_idx = int(str(actividad.respuesta_correcta).strip())

                if actividad.opciones and \
                   0 <= respuesta_usuario_idx < len(actividad.opciones) and \
                   respuesta_usuario_idx == respuesta_correcta_idx:
                    puntuacion_obtenida = actividad.puntos
                    completado = True
            except (ValueError, TypeError):
                # Si la respuesta enviada no es un entero válido, simplemente no se califica
                pass

        elif actividad.tipo_actividad == 'completar_espacios':
            if actividad.respuesta_correcta and respuesta_enviada:
                # Normalizar palabras requeridas
                required_words = [word.strip().lower() for word in actividad.respuesta_correcta.split(',') if word.strip()]
                # Normalizar respuesta del usuario
                user_response_norm = str(respuesta_enviada).strip().lower()

                # Verificar si todas las palabras requeridas están en la respuesta del usuario
                if all(word in user_response_norm for word in required_words):
                    puntuacion_obtenida = actividad.puntos
                    completado = True

        progreso_actividad.puntuacion = puntuacion_obtenida
        progreso_actividad.completado = completado
        
        # Eliminamos la lógica de fecha_completado de aquí, ahora está en el modelo ProgresoActividad.save()
        # if completado and not progreso_actividad.fecha_completado:
        #     progreso_actividad.fecha_completado = timezone.now()

        progreso_actividad.save() # Llama al método save del modelo, que ahora maneja fecha_completado

        serializer = ProgresoActividadSerializer(progreso_actividad)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --- VIEWSETS DE PROGRESO ---

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
        elif usuario_id := self.request.data.get('usuario'):
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save(usuario=self.request.user)

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
        elif (usuario_id := self.request.data.get('usuario')):
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
        elif usuario_id := self.request.data.get('usuario'):
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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return ProgresoActividad.objects.all().order_by('-fecha_inicio')
        return ProgresoActividad.objects.filter(usuario=self.request.user).order_by('-fecha_inicio')

    def perform_create(self, serializer):
        actividad_id = self.request.data.get('actividad')
        if not actividad_id:
            raise serializers.ValidationError({"actividad": "Este campo es requerido."})

        # La corrección para el FieldError:
        if ProgresoActividad.objects.filter(usuario=self.request.user, actividad_id=actividad_id).exists():
            raise serializers.ValidationError({"non_field_errors": ["Ya tienes progreso para esta actividad."]})

        if not self.request.user.is_staff:
            serializer.save(usuario=self.request.user)
        elif usuario_id := self.request.data.get('usuario'):
            serializer.save(usuario_id=usuario_id)
        else:
            serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        # Ya no necesitamos la lógica de fecha_completado aquí, está en el método save del modelo.
        serializer.save() # Guarda los campos que vienen en la petición

        if not self.request.user.is_staff and serializer.instance.usuario != self.request.user:
            raise permissions.PermissionDenied("No tienes permiso para actualizar el progreso de otro usuario.")

    def perform_destroy(self, instance):
        if not self.request.user.is_staff and instance.usuario != self.request.user:
            raise permissions.PermissionDenied("No tienes permiso para eliminar el progreso de otro usuario.")
        instance.delete()