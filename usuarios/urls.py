# usuarios/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, PerfilUsuarioViewSet, PreferenciasAccesibilidadViewSet, RegisterView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'perfiles', PerfilUsuarioViewSet)
router.register(r'preferencias-accesibilidad', PreferenciasAccesibilidadViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
]               