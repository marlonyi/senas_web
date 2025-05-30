# gamificacion/views.py
from rest_framework import viewsets, permissions, generics, mixins, status
from rest_framework.response import Response
from django.utils import timezone # Añade esta importación
from django.db import transaction # Añade esta importación
import logging # Añade esta importación si no la tienes

from .models import PuntosUsuario, Insignia, InsigniaUsuario, Nivel
from .serializers import PuntosUsuarioSerializer, InsigniaSerializer, InsigniaUsuarioSerializer, LeaderboardUserSerializer
from django.contrib.auth.models import User
from .signals import PUNTOS_POR_LOGIN_DIARIO # Asegúrate de que esta importación sea correcta

logger = logging.getLogger(__name__) # Obtener el logger para esta vista


class PuntosUsuarioViewSet(viewsets.GenericViewSet,
                            mixins.RetrieveModelMixin, # Para permitir GET por ID
                            mixins.ListModelMixin):    # Para permitir GET de lista

    queryset = PuntosUsuario.objects.all()
    serializer_class = PuntosUsuarioSerializer
    permission_classes = [permissions.IsAuthenticated] # Asegura que solo usuarios autenticados pueden acceder

    def retrieve(self, request, *args, **kwargs):
        # Obtener la instancia de PuntosUsuario.
        # get_object() ya maneja el 404 si no se encuentra.
        instance = self.get_object()

        # --- Lógica de Puntos Diarios (movida del middleware) ---
        # Aseguramos que el usuario autenticado es el propietario de los PuntosUsuario
        if request.user.is_authenticated and request.user == instance.usuario:
            today = timezone.localdate(timezone.now())
            logger.debug(f"DEBUG (Vista): today (localdate): {today}")

            try:
                with transaction.atomic():
                    # Aquí, 'instance' es el objeto PuntosUsuario recuperado
                    db_last_reward_date = instance.last_daily_reward_date
                    logger.debug(f"DEBUG (Vista): last_daily_reward_date de DB: {db_last_reward_date}")

                    if not db_last_reward_date or db_last_reward_date < today:
                        logger.debug("DEBUG (Vista): Condición de puntos diarios CUMPLIDA. Otorgando puntos...")
                        instance.puntos += PUNTOS_POR_LOGIN_DIARIO
                        instance.last_daily_reward_date = today
                        instance.save(update_fields=['puntos', 'last_daily_reward_date'])
                        logger.debug(f"{request.user.username} ha recibido {PUNTOS_POR_LOGIN_DIARIO} puntos por login diario. Total: {instance.puntos}")
                    else:
                        logger.debug("DEBUG (Vista): Condición de puntos diarios NO CUMPLIDA. No se otorgan puntos.")
            except Exception as e:
                logger.error(f"ERROR (Vista): Fallo al otorgar puntos diarios a {request.user.username}: {e}")
        # --- Fin Lógica de Puntos Diarios ---

        # Continuar con el comportamiento normal de retrieve
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # Si quieres que el usuario solo pueda ver sus propios puntos al listar:
    def get_queryset(self):
        # Para el listado de puntos, si es staff, ve todos, sino, solo los suyos.
        if self.request.user.is_staff:
            return PuntosUsuario.objects.all()
        return PuntosUsuario.objects.filter(usuario=self.request.user)

# Las demás ViewSets siguen igual
class InsigniaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Insignia.objects.all()
    serializer_class = InsigniaSerializer
    permission_classes = [permissions.IsAuthenticated]

class InsigniaUsuarioViewSet(viewsets.ReadOnlyModelViewSet):
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