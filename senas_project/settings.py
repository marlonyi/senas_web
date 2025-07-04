"""
Django settings for senas_project project.

Generated by 'django-admin startproject' using Django 5.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
from corsheaders.defaults import default_headers, default_methods


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-)c178*b$ec!h&#(h=629yk2tqb!7@yd*2q4_$i*$t)xm!2jh^0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# =====================
# CONFIGURACIÓN DE CORS
# =====================

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # React en modo desarrollo (vite)
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "Content-Type",
    "Authorization",
]

CORS_ALLOW_METHODS = list(default_methods)



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'drf_spectacular',
    'usuarios',
    'cursos.apps.CursosConfig',
    'traducciones',
    'comunidad',
    'gamificacion.apps.GamificacionConfig',
    'accesibilidad',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', # <-- Aquí
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'senas_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'senas_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'señas_db',         
        'USER': 'postgres',     
        'PASSWORD': '12345', 
        'HOST': 'localhost',        
        'PORT': '5432',           
    }
}
# The `REST_FRAMEWORK` settings in Django are used to configure the behavior of the Django REST
# framework, which is a powerful and flexible toolkit for building Web APIs in Django. Let's break
# down the key components of this configuration:
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated', # <--- Cambia a IsAuthenticated
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'API de Plataforma de LSC', # Un título descriptivo para tu API
    'DESCRIPTION': 'Documentación de la API REST para el sistema de aprendizaje de Lengua de Señas Colombiana. Incluye módulos, lecciones, actividades, progreso de usuario y más.', # Una descripción más detallada
    'VERSION': '1.0.0', # La versión actual de tu API
    'SERVE_INCLUDE_SCHEMA': False, # No servir el esquema JSON/YAML directamente si no lo necesitas separado
    'SWAGGER_UI_DIST': 'SIDECAR', # Utiliza la distribución de Swagger UI localmente para mejor rendimiento
    'SWAGGER_UI_FAVICON_HREF': 'https://www.djangoproject.com/favicon.ico', # Opcional: puedes poner el favicon de Django o uno propio
    'REDOC_UI_DIST': 'SIDECAR', # Utiliza la distribución de Redoc localmente
    # Puedes añadir más configuraciones aquí, por ejemplo:
    # 'COMPONENT_SPLIT_REQUEST': True, # Para dividir el esquema en componentes más pequeños
    # 'SECURITY': [{'BearerAuth': []}], # Si quieres que Swagger/Redoc muestre la opción de autenticación JWT
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1), # Tiempo de vida del token de acceso
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),   # Tiempo de vida del token de refresco
    'ROTATE_REFRESH_TOKENS': True, # Si se deben rotar los tokens de refresco
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY, # Usa la SECRET_KEY de tu proyecto
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# senas_project/settings.py

# ... (resto de tu archivo settings.py)

# Configuración de Archivos Estáticos (STATIC_URL ya existe)
STATIC_URL = 'static/' # Ya debería estar ahí

# Directorio donde Django recolectará todos los archivos estáticos para producción
# No debe ser el mismo que STATICFILES_DIRS
STATIC_ROOT = BASE_DIR / 'staticfiles' # Esto creará una carpeta 'staticfiles' en la raíz de tu proyecto

# Directorios adicionales donde Django buscará archivos estáticos (para desarrollo, si tus apps tienen static)
STATICFILES_DIRS = [
    # BASE_DIR / 'static_dev', # Ejemplo: si tuvieras una carpeta 'static_dev' global para tu proyecto
]

# ... (alrededor de la sección de STATIC_FILES, o al final del archivo)

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración para archivos subidos por el usuario (MEDIA)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media' # Esto creará una carpeta 'media' en la raíz de tu proyecto



# Configuración de Logging para ver los mensajes de depuración en la consola
# Asegúrate de añadir esto si no tienes ya una sección LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',  # <--- ¡AÑADE ESTO!
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',  # <--- ¡AÑADE ESTO!
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'gamificacion': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'cursos': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
