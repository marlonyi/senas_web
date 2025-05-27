# cursos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# --- Importar los nuevos ViewSets de progreso ---
from .views import CursoViewSet, ModuloViewSet, LeccionViewSet, ActividadViewSet, ProgresoCursoViewSet, ProgresoModuloViewSet, ProgresoLeccionViewSet, ProgresoActividadViewSet

router = DefaultRouter()
router.register(r'cursos', CursoViewSet)
router.register(r'modulos', ModuloViewSet)
router.register(r'lecciones', LeccionViewSet)
router.register(r'actividades', ActividadViewSet)
# --- Registrar los nuevos ViewSets de progreso ---
router.register(r'progreso-cursos', ProgresoCursoViewSet)
router.register(r'progreso-modulos', ProgresoModuloViewSet)
router.register(r'progreso-lecciones', ProgresoLeccionViewSet)
router.register(r'progreso-actividades', ProgresoActividadViewSet)


urlpatterns = [
    path('', include(router.urls)),
]