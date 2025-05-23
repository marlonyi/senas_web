# gamificacion/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LogroViewSet, LogroUsuarioViewSet

router = DefaultRouter()
router.register(r'logros', LogroViewSet)
router.register(r'logros-usuario', LogroUsuarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]