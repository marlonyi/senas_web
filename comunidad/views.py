# comunidad/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Autenticado para crear/editar, cualquiera para listar/ver

    def perform_create(self, serializer):
        # Asigna el creador del foro al usuario autenticado
        serializer.save(creador=self.request.user)

    def perform_update(self, serializer):
        # Solo permite al creador del foro actualizarlo
        if serializer.instance.creador != self.request.user:
            raise permissions.PermissionDenied("No tienes permiso para editar este foro.")
        serializer.save()

    def perform_destroy(self, instance):
        # Solo permite al creador del foro eliminarlo
        if instance.creador != self.request.user:
            raise permissions.PermissionDenied("No tienes permiso para eliminar este foro.")
        instance.delete()

    # Acción personalizada para obtener los comentarios de un foro específico
    # Esto creará una URL como /foros/{pk}/comentarios/
    @action(detail=True, methods=['get', 'post'], url_path='comentarios',
            serializer_class=ComentarioSerializer,
            permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def comentarios(self, request, pk=None):
        foro = self.get_object() # Obtiene el foro actual

        if request.method == 'POST':
            # Crear un nuevo comentario para este foro
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # --> ¡AQUÍ ES DONDE SE ASIGNA EL FORO! <--
            serializer.save(autor=request.user, foro=foro)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
        # --- INICIO DE LA MODIFICACIÓN ---
        # Lógica para GET (listar comentarios del foro)
        # Obtener solo comentarios de nivel superior (main comments) para este foro
        queryset = foro.comentarios.filter(parent_comentario__isnull=True).order_by('fecha_creacion')
        
        # Serializar el queryset
        serializer = self.get_serializer(queryset, many=True)
        
        # --- AÑADE ESTA LÍNEA ---
        return Response(serializer.data) # ¡Aquí es donde se devuelve la respuesta para GET!
        # --- FIN DE LA MODIFICACIÓN ---



class ComentarioViewSet(viewsets.ModelViewSet):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Asigna el autor del comentario al usuario autenticado
        # NOTA: El 'foro' debe ser provisto en el request body al crear un comentario
        # o se asume que viene de una URL anidada si se usa el @action en ForoViewSet
        serializer.save(autor=self.request.user)

    def perform_update(self, serializer):
        # Solo permite al autor del comentario actualizarlo
        if serializer.instance.autor != self.request.user:
            raise permissions.PermissionDenied("No tienes permiso para editar este comentario.")
        serializer.save()

    def perform_destroy(self, instance):
        # Solo permite al autor del comentario eliminarlo
        if instance.autor != self.request.user:
            raise permissions.PermissionDenied("No tienes permiso para eliminar este comentario.")
        instance.delete()
    
    # Acción personalizada para dar/quitar "Me Gusta" a un comentario
    # Esto creará una URL como /comentarios/{pk}/likes/
    @action(detail=True, methods=['post', 'delete'], url_path='likes',
            permission_classes=[permissions.IsAuthenticated])
    def likes(self, request, pk=None):
        comentario = self.get_object() # Obtiene el comentario actual
        usuario = request.user

        if request.method == 'POST':
            # Dar "Me Gusta"
            if MeGustaComentario.objects.filter(comentario=comentario, usuario=usuario).exists():
                return Response({"detail": "Ya le diste 'Me Gusta' a este comentario."},
                                status=status.HTTP_409_CONFLICT)
            MeGustaComentario.objects.create(comentario=comentario, usuario=usuario)
            return Response({"detail": "Me Gusta añadido exitosamente."}, status=status.HTTP_201_CREATED)
        
        elif request.method == 'DELETE':
            # Quitar "Me Gusta"
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
    permission_classes = [permissions.IsAuthenticated] # Solo usuarios autenticados pueden ver/crear/eliminar likes

    def perform_create(self, serializer):
        # Asigna el usuario que dio el like
        # NOTA: El 'comentario' debe ser provisto en el request body
        serializer.save(usuario=self.request.user)

    def get_queryset(self):
        # Opcional: solo permitir a los usuarios ver sus propios likes, o todos si es admin
        if self.request.user.is_staff: # Ejemplo: admins pueden ver todos los likes
            return MeGustaComentario.objects.all()
        return MeGustaComentario.objects.filter(usuario=self.request.user)