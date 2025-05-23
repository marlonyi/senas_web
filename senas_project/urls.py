# senas_project/urls.py
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView, # Opcional: para verificar un token
)   

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # path('admin/', admin.site.urls), # Puedes mantenerla comentada si no la usas
    path('api/usuarios/', include('usuarios.urls')),
    path('api/', include('cursos.urls')),
    path('api/traducciones/', include('traducciones.urls')),
    path('api/comunidad/', include('comunidad.urls')),
    path('api/gamificacion/', include('gamificacion.urls')),

    # Rutas de autenticación JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'), # Opcional
    
    # Rutas de documentación de la API (Spectacular) <--- ¡AÑADE ESTAS LÍNEAS!
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'), # El esquema OpenAPI en sí (JSON/YAML)
    # IU de Swagger: http://127.0.0.1:8000/api/schema/swagger-ui/
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # IU de Redoc: http://127.0.0.1:8000/api/schema/redoc/
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]