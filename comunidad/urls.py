# comunidad/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ForoViewSet, ComentarioViewSet, MeGustaComentarioViewSet

router = DefaultRouter()
router.register(r'foros', ForoViewSet)
router.register(r'comentarios', ComentarioViewSet)
router.register(r'me-gustas-comentario', MeGustaComentarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]