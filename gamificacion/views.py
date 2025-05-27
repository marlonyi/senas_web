# gamificacion/views.py
from rest_framework import viewsets, permissions
from .models import PuntosUsuario, Insignia, InsigniaUsuario # <-- ¡Esta línea es CRUCIAL!
from .serializers import PuntosUsuarioSerializer, InsigniaSerializer, InsigniaUsuarioSerializer

class PuntosUsuarioViewSet(viewsets.ReadOnlyModelViewSet):
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