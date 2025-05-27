# senas_project/urls.py

from django.urls import path, include
from django.contrib import admin # Asegúrate de que esta importación esté presente
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView, # Opcional: para verificar un token
)   

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls), # <--- ¡DESCOMENTA ESTA LÍNEA!
    path('api/usuarios/', include('usuarios.urls')),
    path('api/', include('cursos.urls')),
    path('api/traducciones/', include('traducciones.urls')),
    path('api/comunidad/', include('comunidad.urls')),
    path('api/gamificacion/', include('gamificacion.urls')),

    # Rutas de autenticación JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'), # Opcional
    
    # Rutas de documentación de la API (Spectacular)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]