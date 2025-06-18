# accesibilidad/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CaracteristicaContenidoAccesibleViewSet, PreferenciaUsuarioAccesibilidadViewSet

router = DefaultRouter()
router.register(r'caracteristicas-contenido', CaracteristicaContenidoAccesibleViewSet)
router.register(r'preferencias-usuario', PreferenciaUsuarioAccesibilidadViewSet)

urlpatterns = [
    path('', include(router.urls)),
]