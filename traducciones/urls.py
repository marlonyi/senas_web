# traducciones/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaSendaViewSet, SendaViewSet

router = DefaultRouter()
router.register(r'categorias-senda', CategoriaSendaViewSet)
router.register(r'sendas', SendaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]