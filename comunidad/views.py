# comunidad/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Foro, Comentario, MeGustaComentario
from .serializers import (
    ForoSerializer,
    ComentarioSerializer,
    MeGustaComentarioSerializer,
    UserSerializerForCommunity
)

class ForoViewSet(viewsets.ModelViewSet):
    queryset = Foro.objects.all()
    serializer_class = ForoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # --- FILTRADO Y BÚSQUEDA PARA FOROS ---
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['activo', 'creador__username'] # Filtrar por estado activo o creador
    search_fields = ['titulo', 'descripcion'] # Buscar por título o descripción
    # ------------------------------------

    def perform_create(self, serializer):
        serializer.save(creador=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.creador != self.request.user:
            raise permissions.PermissionDenied("No tienes permiso para editar este foro.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.creador != self.request.user:
            raise permissions.PermissionDenied("No tienes permiso para eliminar este foro.")
        instance.delete()

    @action(detail=True, methods=['get', 'post'], url_path='comentarios',
                    serializer_class=ComentarioSerializer,
                    permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def comentarios(self, request, pk=None):
        foro = self.get_object()

        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(autor=request.user, foro=foro)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        queryset = foro.comentarios.filter(parent_comentario__isnull=True).order_by('fecha_creacion')

        # --- APLICAR FILTROS Y BÚSQUEDA A LOS COMENTARIOS DE LA ACCIÓN ---
        # Aunque la acción es anidada, puedes aplicar filtrado aquí.
        # Puedes usar DjangoFilterBackend directamente en el queryset si lo deseas,
        # pero para búsquedas simples en una acción personalizada, puedes filtrar manualmente.
        # No obstante, para mantener la coherencia y aprovechar los backends,
        # lo más limpio es crear un ComentarioFilterSet y aplicarlo.
        # Por simplicidad aquí, si la complejidad es baja, podríamos filtrar manualmente.
        # Para esta acción específica, el filtrado y búsqueda del ViewSet principal no se aplican directamente,
        # se deberían implementar aquí si se desean.
        # Por ahora, dejaremos esta acción sin filtrado/búsqueda avanzado,
        # y los ViewSet de Comentario y Foro tendrán su propio filtrado.
        # Si quieres filtrado aquí, tendríamos que crear un filterset.
        # Por ahora, nos centraremos en el ViewSet de Comentario para el filtrado general.
        # -----------------------------------------------------------------

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ComentarioViewSet(viewsets.ModelViewSet):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # --- FILTRADO Y BÚSQUEDA PARA COMENTARIOS ---
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['foro', 'autor__username', 'parent_comentario'] # Filtrar por foro, autor o si es respuesta
    search_fields = ['contenido'] # Buscar por contenido del comentario
    # ------------------------------------------

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.autor != self.request.user:
            raise permissions.PermissionDenied("No tienes permiso para editar este comentario.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.autor != self.request.user:
            raise permissions.PermissionDenied("No tienes permiso para eliminar este comentario.")
        instance.delete()

    @action(detail=True, methods=['post', 'delete'], url_path='likes',
                    permission_classes=[permissions.IsAuthenticated])
    def likes(self, request, pk=None):
        comentario = self.get_object()
        usuario = request.user

        if request.method == 'POST':
            if MeGustaComentario.objects.filter(comentario=comentario, usuario=usuario).exists():
                return Response({"detail": "Ya le diste 'Me Gusta' a este comentario."},
                                status=status.HTTP_409_CONFLICT)
            MeGustaComentario.objects.create(comentario=comentario, usuario=usuario)
            return Response({"detail": "Me Gusta añadido exitosamente."}, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            try:
                me_gusta = MeGustaComentario.objects.get(comentario=comentario, usuario=usuario)
                me_gusta.delete()
                return Response({"detail": "Me Gusta eliminado exitosamente."}, status=status.HTTP_204_NO_CONTENT)
            except MeGustaComentario.DoesNotExist:
                return Response({"detail": "No has dado 'Me Gusta' a este comentario."},
                                status=status.HTTP_404_NOT_FOUND)


class MeGustaComentarioViewSet(viewsets.ModelViewSet):
    queryset = MeGustaComentario.objects.all()
    serializer_class = MeGustaComentarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    # --- FILTRADO PARA ME GUSTA ---
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['comentario', 'usuario'] # Filtrar por comentario o usuario
    # ----------------------------

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def get_queryset(self):
        if self.request.user.is_staff:
            return MeGustaComentario.objects.all()
        return MeGustaComentario.objects.filter(usuario=self.request.user)