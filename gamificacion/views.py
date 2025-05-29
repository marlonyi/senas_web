from rest_framework import viewsets, permissions, generics # Importamos generics
from .models import PuntosUsuario, Insignia, InsigniaUsuario, Nivel # Importamos Nivel
from .serializers import PuntosUsuarioSerializer, InsigniaSerializer, InsigniaUsuarioSerializer, LeaderboardUserSerializer # Importamos todos los serializadores necesarios
from django.contrib.auth.models import User # Importamos User

# Para la vista de prueba temporal
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

class PuntosUsuarioViewSet(viewsets.ModelViewSet):
    """
    API para ver los puntos de los usuarios.
    """
    queryset = PuntosUsuario.objects.all()
    serializer_class = PuntosUsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return PuntosUsuario.objects.all()
        return PuntosUsuario.objects.filter(usuario=self.request.user)

class InsigniaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para ver las insignias disponibles.
    """
    queryset = Insignia.objects.all()
    serializer_class = InsigniaSerializer
    permission_classes = [permissions.IsAuthenticated]

class InsigniaUsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para ver las insignias obtenidas por los usuarios.
    """
    queryset = InsigniaUsuario.objects.all()
    serializer_class = InsigniaUsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return InsigniaUsuario.objects.all()
        return InsigniaUsuario.objects.filter(usuario=self.request.user)
    
class LeaderboardView(generics.ListAPIView):
    serializer_class = LeaderboardUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(puntos_gamificacion__isnull=False).order_by('-puntos_gamificacion__puntos')
