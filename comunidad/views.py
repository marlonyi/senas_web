# comunidad/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Foro, Comentario, MeGustaComentario
from .serializers import ForoSerializer, ComentarioSerializer, MeGustaComentarioSerializer
from django.db.models import F

class ForoViewSet(viewsets.ModelViewSet):
    queryset = Foro.objects.all()
    serializer_class = ForoSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Solo los usuarios autenticados pueden crear foros.
            # Puedes cambiar a IsAdminUser si solo los administradores pueden crear/modificar.
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            # Todos los usuarios autenticados pueden ver los foros
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Asocia el creador del foro al usuario autenticado
        serializer.save(creador=self.request.user)

class ComentarioViewSet(viewsets.ModelViewSet):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Solo los usuarios autenticados pueden crear/modificar/eliminar comentarios
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            # Todos los usuarios autenticados pueden ver los comentarios
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Asocia el autor del comentario al usuario autenticado
        serializer.save(autor=self.request.user)

    # Accion personalizada para responder a un comentario
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def responder(self, request, pk=None):
        parent_comentario = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(autor=request.user, foro=parent_comentario.foro, parent_comentario=parent_comentario)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MeGustaComentarioViewSet(viewsets.ModelViewSet):
    queryset = MeGustaComentario.objects.all()
    serializer_class = MeGustaComentarioSerializer
    permission_classes = [permissions.IsAuthenticated] # Solo usuarios autenticados pueden gestionar likes

    def get_queryset(self):
        # Opcional: Solo ver los likes que ha dado el usuario actual, o todos?
        # Por defecto, ver todos los likes para contar si es necesario.
        return MeGustaComentario.objects.all()

    def perform_create(self, serializer):
        # Asocia el usuario que da "Me Gusta"
        comentario_id = self.request.data.get('comentario')
        comentario = get_object_or_404(Comentario, id=comentario_id)

        # Evitar duplicados: Un usuario solo puede dar un like a un comentario
        if MeGustaComentario.objects.filter(comentario=comentario, usuario=self.request.user).exists():
            return Response({"detail": "Ya has dado 'Me Gusta' a este comentario."}, status=status.HTTP_409_CONFLICT)

        serializer.save(usuario=self.request.user, comentario=comentario)

    # Para permitir eliminar el "Me Gusta"
    def perform_destroy(self, instance):
        # Asegura que solo el usuario que dio el like puede eliminarlo
        if instance.usuario != self.request.user:
            return Response({"detail": "No tienes permiso para eliminar este 'Me Gusta'."}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()