# gamificacion/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PuntosUsuarioViewSet, InsigniaViewSet, InsigniaUsuarioViewSet # <-- ¡Esta línea es CRUCIAL!

router = DefaultRouter()
router.register(r'puntos', PuntosUsuarioViewSet)
router.register(r'insignias', InsigniaViewSet)
router.register(r'insignias-usuario', InsigniaUsuarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]