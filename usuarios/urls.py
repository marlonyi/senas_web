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
    # URLs generadas por el router para los ViewSets
    path('', include(router.urls)),

    # Autenticación con JWT (JSON Web Tokens) - Los tienes en senas_project/urls.py,
    # pero a menudo se duplican aquí si quieres un grupo de URLs de autenticación centralizado
    # o si los router.urls ya ocupan la raíz de 'usuarios/'.
    # Para evitar duplicados y mantenerlo limpio, los mantendré centralizados en senas_project/urls.py
    # Pero si quieres que 'api/usuarios/token/' funcione en vez de 'api/token/', podrías moverlos aquí.
    # Por ahora, los dejaremos en el root del proyecto como los tenías.

    # Registro de usuario
    path('register/', RegisterView.as_view(), name='user_register'), # Nombre cambiado para claridad

    # Gestión del perfil del usuario autenticado (MiPerfilView)
    # Permite GET para ver el perfil y PUT/PATCH para actualizar
    path('mi-perfil/', MiPerfilView.as_view(), name='mi_perfil'),

    # Actualización específica del avatar
    path('mi-perfil/avatar/', AvatarUpdateView.as_view(), name='update_avatar'),

    # Cambio de contraseña
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # Puedes añadir más URLs aquí según sea necesario (ej. recuperación de contraseña, etc.)
]