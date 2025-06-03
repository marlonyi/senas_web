from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, generics, mixins, status
from rest_framework import serializers # Importado explícitamente para serializers.ValidationError

# Importa CategoriaCurso aquí
from .models import PuntosUsuario, Insignia, InsigniaUsuario, Nivel
# Importa CategoriaCursoSerializer
from .serializers import PuntosUsuarioSerializer, InsigniaSerializer, InsigniaUsuarioSerializer, LeaderboardUserSerializer, NivelSerializer # Asegúrate de importar NivelSerializer

from django.contrib.auth import get_user_model # ¡CAMBIO: Usar get_user_model!
from .signals import PUNTOS_POR_LOGIN_DIARIO # Asegúrate de que esta importación sea correcta

from rest_framework.decorators import action
from django.utils import timezone 
import datetime 
from django.db import IntegrityError, transaction # ¡Añadido transaction!
import logging # Añade esta importación si no la tienes

User = get_user_model() # ¡NUEVO: Obtener el modelo de usuario!
logger = logging.getLogger(__name__) # Obtener el logger para esta vista


# ¡NUEVO: ViewSet para el modelo Nivel!
class NivelViewSet(viewsets.ModelViewSet):
    queryset = Nivel.objects.all()
    serializer_class = NivelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser]
        else:
            self.permission_classes = [permissions.AllowAny] 
        return super().get_permissions()


class PuntosUsuarioViewSet(viewsets.GenericViewSet,
                             mixins.RetrieveModelMixin, # Para permitir GET por ID
                             mixins.ListModelMixin):    # Para permitir GET de lista

    queryset = PuntosUsuario.objects.all()
    serializer_class = PuntosUsuarioSerializer
    permission_classes = [permissions.IsAuthenticated] # Asegura que solo usuarios autenticados pueden acceder

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Aseguramos que el usuario autenticado es el propietario de los PuntosUsuario
        if request.user.is_authenticated and request.user == instance.usuario:
            today = timezone.localdate(timezone.now())
            logger.debug(f"DEBUG (Vista): today (localdate): {today}")
            logger.debug(f"DEBUG (Vista): Current instance points: {instance.puntos}, last_daily_login_award: {instance.last_daily_login_award}, nivel_actual: {instance.nivel_actual}")

            try:
                with transaction.atomic():
                    db_last_reward_date = instance.last_daily_login_award 
                    logger.debug(f"DEBUG (Vista): last_daily_login_award from DB: {db_last_reward_date}")

                    fields_to_update = [] # Lista para guardar qué campos necesitan ser actualizados

                    if not db_last_reward_date or db_last_reward_date < today:
                        logger.debug("DEBUG (Vista): Daily points condition MET. Granting points...")
                        instance.puntos += PUNTOS_POR_LOGIN_DIARIO
                        instance.last_daily_login_award = today
                        fields_to_update.extend(['puntos', 'last_daily_login_award'])
                        logger.debug(f"{request.user.username} received {PUNTOS_POR_LOGIN_DIARIO} points for daily login. Total: {instance.puntos}")
                    else:
                        logger.debug("DEBUG (Vista): Daily points condition NOT MET. No points granted.")

                    # ¡IMPORTANTE! Llama a la lógica de actualización de nivel DESPUÉS de que los puntos puedan haber cambiado
                    level_changed = instance.update_nivel_based_on_points() # Esto actualiza instance.nivel_actual en memoria
                    if level_changed:
                        fields_to_update.append('nivel_actual')
                        logger.debug(f"DEBUG (Vista): Level changed to {instance.nivel_actual.nombre if instance.nivel_actual else 'None'}")

                    # Solo guarda si hay campos que necesitan ser actualizados
                    if fields_to_update: 
                        instance.save(update_fields=fields_to_update)
                        logger.debug(f"DEBUG (Vista): Saved fields: {fields_to_update}")
                    else:
                        logger.debug("DEBUG (Vista): No fields to update.")

            except Exception as e:
                logger.error(f"ERROR (Vista): Failed to grant daily points or update level for {request.user.username}: {e}")

        # Continuar con el comportamiento normal de retrieve
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        if self.request.user.is_staff:
            return PuntosUsuario.objects.all()
        return PuntosUsuario.objects.filter(usuario=self.request.user)

# Las demás ViewSets siguen igual
class InsigniaViewSet(viewsets.ModelViewSet): # ¡CORREGIDO: ModelViewSet!
    queryset = Insignia.objects.all()
    serializer_class = InsigniaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Permite lectura a todos, escritura solo a autenticados

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser] # Solo admins pueden crear/editar/eliminar
        else:
            self.permission_classes = [permissions.AllowAny] # Cualquiera puede ver las insignias
        return super().get_permissions()


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
        # Asegúrate de que solo los usuarios con un PuntosUsuario asociado aparezcan en el leaderboard
        return User.objects.filter(puntos_gamificacion__isnull=False).select_related('puntos_gamificacion__nivel_actual').order_by('-puntos_gamificacion__puntos')