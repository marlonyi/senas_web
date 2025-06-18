# usuarios/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    UserViewSet,
    PerfilUsuarioViewSet,
    PreferenciasAccesibilidadViewSet,
    RegisterView,
    MiPerfilView,        # Nueva vista
    AvatarUpdateView,     # Nueva vista
    ChangePasswordView,   # Nueva vista
    LogoutView,         # Nueva vista
)

# Creamos un router para los ViewSets
# Nota: UserViewSet, PerfilUsuarioViewSet y PreferenciasAccesibilidadViewSet
# se usarán principalmente para administradores o casos específicos.
# La gestión del propio perfil del usuario se hará a través de MiPerfilView.
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'perfiles', PerfilUsuarioViewSet)
router.register(r'preferencias-accesibilidad', PreferenciasAccesibilidadViewSet)


urlpatterns = [
    
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='user_register'), # Nombre cambiado para claridad
    path('mi-perfil/', MiPerfilView.as_view(), name='mi_perfil'),
    path('logout/', LogoutView.as_view(), name='logout'), 
    path('mi-perfil/avatar/', AvatarUpdateView.as_view(), name='update_avatar'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]