# cursos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CursoViewSet, LeccionViewSet, ActividadViewSet, ProgresoUsuarioViewSet, ModuloViewSet # Asegúrate de importar ModuloViewSet

router = DefaultRouter()
router.register(r'cursos', CursoViewSet)
router.register(r'modulos', ModuloViewSet) # <--- ¡Añade esta línea!
router.register(r'lecciones', LeccionViewSet)
router.register(r'actividades', ActividadViewSet)
router.register(r'progreso-usuario', ProgresoUsuarioViewSet)




urlpatterns = [
    path('', include(router.urls)),
]