# 📚 API de Plataforma de Aprendizaje de Lengua de Señas Colombiana (LSC)

Este repositorio contiene la implementación de la API REST para una plataforma interactiva de aprendizaje de Lengua de Señas Colombiana (LSC). Desarrollada con Django REST Framework, esta API gestiona usuarios, cursos, módulos, lecciones, actividades y el progreso del usuario, proporcionando una base sólida para una aplicación web o móvil.

## ✨ Características Principales

* **Gestión de Cursos:** Crea, lee, actualiza y elimina cursos estructurados por niveles.
* **Módulos y Lecciones:** Organización de contenido de cursos en módulos y lecciones detalladas.
* **Actividades Interactivas:** Soporte para diferentes tipos de actividades asociadas a lecciones.
* **Seguimiento de Progreso:** Registro del progreso del usuario en lecciones y actividades, incluyendo estado de completado, puntuación e intentos.
* **Autenticación Segura:** Implementación de JWT (JSON Web Tokens) para un acceso seguro a la API.
* **Permisos Granulares:** Control de acceso a los recursos de la API basado en roles de usuario (autenticado, administrador).
* **Filtrado Avanzado:** Posibilidad de filtrar listados de recursos (ej., cursos por nivel, módulos por curso).
* **Búsqueda de Texto:** Funcionalidad de búsqueda para encontrar recursos por nombre o descripción.
* **Paginación Eficiente:** Paginación de resultados para manejar grandes volúmenes de datos.
* **Documentación Interactiva (Swagger/Redoc):** Documentación de API generada automáticamente, interactiva y accesible vía web, facilitando la exploración y prueba de endpoints.

## 🚀 Cómo Empezar

Sigue estos pasos para configurar y ejecutar el proyecto en tu máquina local.

### 📋 Prerrequisitos

Asegúrate de tener instalado lo siguiente:

* **Python 3.x**
* **pip** (el gestor de paquetes de Python)

### 💻 Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/tu-repositorio.git](https://github.com/tu-usuario/tu-repositorio.git)
    cd tu-repositorio # Navega a la raíz del proyecto
    ```
    *(Reemplaza `tu-usuario/tu-repositorio.git` con la URL real de tu repositorio.)*

2.  **Crear y activar un entorno virtual:**
    * **Windows:**
        ```bash
        python -m venv venv_señas_backend
        venv_señas_backend\Scripts\activate
        ```
    * **Linux/macOS:**
        ```bash
        python3 -m venv venv_señas_backend
        source venv_señas_backend/bin/activate
        ```

3.  **Instalar las dependencias de Python:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Si no tienes `requirements.txt` aún, puedes generarlo con `pip freeze > requirements.txt` después de instalar todas las librerías mencionadas en los pasos de instalación inicial en nuestro chat, como `django`, `djangorestframework`, `djangorestframework-simplejwt`, `django-filter`, `drf-spectacular`)*

4.  **Configurar la base de datos:**
    * Generar migraciones (si es la primera vez o has modificado modelos):
        ```bash
        python manage.py makemigrations
        ```
    * Aplicar migraciones:
        ```bash
        python manage.py migrate
        ```

5.  **Crear un superusuario (para acceder al panel de administración y probar la API):**
    ```bash
    python manage.py createsuperuser
    ```
    * Sigue las instrucciones en pantalla para crear tu usuario admin.

6.  **Iniciar el servidor de desarrollo:**
    ```bash
    python manage.py runserver
    ```
    * La API estará disponible en `http://127.0.0.1:8000/`.

## 📄 Documentación de la API

Una vez que el servidor esté en ejecución, puedes acceder a la documentación interactiva de la API:

* **Swagger UI:** [http://127.0.0.1:8000/api/schema/swagger-ui/](http://127.0.0.1:8000/api/schema/swagger-ui/)
* **Redoc:** [http://127.0.0.1:8000/api/schema/redoc/](http://127.0.0.1:8000/api/schema/redoc/)

Aquí podrás ver todos los endpoints disponibles, sus métodos, parámetros y modelos de respuesta, así como probar las llamadas a la API directamente desde el navegador.

## 🤝 Contribución

Si deseas contribuir a este proyecto, por favor sigue estos pasos:

1.  Haz un "fork" del repositorio.
2.  Crea una nueva rama (`git checkout -b feature/nueva-caracteristica`).
3.  Realiza tus cambios y asegúrate de que pasen las pruebas.
4.  Haz commit de tus cambios (`git commit -m 'feat: Añade nueva característica X'`).
5.  Sube tu rama (`git push origin feature/nueva-caracteristica`).
6.  Abre un Pull Request.

## 📞 Contacto

Para cualquier pregunta o sugerencia, puedes contactarme en [tu_email@example.com] o visitar mi perfil de GitHub [https://github.com/tu_usuario].

---
