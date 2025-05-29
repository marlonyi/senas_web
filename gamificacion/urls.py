from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PuntosUsuarioViewSet, InsigniaViewSet, InsigniaUsuarioViewSet, LeaderboardView

# Inicializa el router
router = DefaultRouter()

# Registra tus ViewSets con sus respectivos prefijos de URL
# CORRECCIÓN: El router no necesita regex para el prefijo, solo la cadena literal.
router.register('puntos-usuario', PuntosUsuarioViewSet, basename='puntos-usuario')
router.register('insignias', InsigniaViewSet, basename='insignia')
router.register('insignias-usuario', InsigniaUsuarioViewSet, basename='insignias-usuario')

# Define los patrones de URL
urlpatterns = [
    # Incluye todas las URLs generadas automáticamente por el router
    path('', include(router.urls)),
    # Agrega la URL para el leaderboard (que es una APIView, no un ViewSet)
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
]