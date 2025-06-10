# senas_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Importa settings
from django.conf.urls.static import static # Importa static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Incluye las URLs de tus aplicaciones API bajo el prefijo 'api/'
    path('api/usuarios/', include('usuarios.urls')),
    path('api/cursos/', include('cursos.urls')),
    path('api/traducciones/', include('traducciones.urls')),
    path('api/comunidad/', include('comunidad.urls')),
    path('api/gamificacion/', include('gamificacion.urls')),
    path('api/accesibilidad/', include('accesibilidad.urls')),

    # Rutas de autenticación JWT (las mantienes aquí en la raíz de 'api/')
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Rutas de documentación de la API (Spectacular)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Servir archivos multimedia (media files) y estáticos en desarrollo
# IMPORTANTE: Esto solo debe usarse en entorno de desarrollo (settings.DEBUG = True).
# En producción, usa un servidor web como Nginx o Apache para servir estos archivos.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Asegura que también sirva estáticos