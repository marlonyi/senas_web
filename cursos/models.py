# cursos/models.py
from django.db import models
from django.contrib.auth.models import User

# ... (Tus modelos Curso, Modulo, Leccion, Actividad permanecen sin cambios) ...

class Curso(models.Model):
    id_curso = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255) # <-- ¡Aquí está! El campo se llama 'nombre', no 'titulo'.
    descripcion = models.TextField()
    nivel = models.CharField(max_length=50)
    imagen_url = models.URLField(max_length=500, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Modulo(models.Model):
    id_modulo = models.AutoField(primary_key=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='modulos')
    nombre = models.CharField(max_length=255) # <-- ¡Aquí está! El campo se llama 'nombre'.
    descripcion = models.TextField()
    orden = models.IntegerField(default=1)

    class Meta:
        ordering = ['orden']
        unique_together = ('curso', 'orden')

    def __str__(self):
        return f"{self.nombre} ({self.curso.nombre})"

class Leccion(models.Model):
    id_leccion = models.AutoField(primary_key=True)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='lecciones')
    titulo = models.CharField(max_length=255) # <-- ¡Aquí está! El campo se llama 'titulo'.
    contenido_texto = models.TextField(blank=True, null=True)
    url_video = models.URLField(max_length=500, blank=True, null=True)
    url_imagen = models.URLField(max_length=500, blank=True, null=True)
    orden = models.IntegerField(default=1)
    class Meta:
        ordering = ['orden']
        unique_together = ('modulo', 'orden')

    def __str__(self):
        return f"{self.titulo} ({self.modulo.nombre})"

class Actividad(models.Model):
    id_actividad = models.AutoField(primary_key=True)
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE, related_name='actividades')
    pregunta = models.TextField()
    opciones = models.JSONField(blank=True, null=True)
    respuesta_correcta = models.TextField(blank=True, null=True)
    puntos = models.IntegerField(default=10)

    TIPO_ACTIVIDAD_CHOICES = [
        ('pregunta_respuesta', 'Pregunta y Respuesta'),
        ('seleccion_multiple', 'Selección Múltiple'),
        ('completar_espacios', 'Completar Espacios'),
    ]
    tipo_actividad = models.CharField(
        max_length=50,
        choices=TIPO_ACTIVIDAD_CHOICES,
        default='pregunta_respuesta'
    )

    def __str__(self):
        return f"Actividad {self.id_actividad} - {self.get_tipo_actividad_display()} de {self.leccion.titulo}"

# --- NUEVOS MODELOS DE PROGRESO ---

class ProgresoCurso(models.Model):
    id_progreso_curso = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    completado = models.BooleanField(default=False)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(blank=True, null=True)
    puntos_otorgados = models.BooleanField(default=False)

    class Meta:
        unique_together = ('usuario', 'curso') # Un solo registro por usuario/curso

    def __str__(self):
        return f"Progreso de {self.usuario.username} en Curso: {self.curso.nombre} - Completado: {self.completado}"

class ProgresoModulo(models.Model):
    id_progreso_modulo = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE)
    completado = models.BooleanField(default=False)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(blank=True, null=True)
    puntos_otorgados = models.BooleanField(default=False)

    class Meta:
        unique_together = ('usuario', 'modulo') # Un solo registro por usuario/modulo

    def __str__(self):
        return f"Progreso de {self.usuario.username} en Módulo: {self.modulo.nombre} - Completado: {self.completado}"

class ProgresoLeccion(models.Model):
    id_progreso_leccion = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE)
    completado = models.BooleanField(default=False)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(blank=True, null=True)
    puntos_otorgados = models.BooleanField(default=False)

    class Meta:
        unique_together = ('usuario', 'leccion') # Un solo registro por usuario/lección

    def __str__(self):
        return f"Progreso de {self.usuario.username} en Lección: {self.leccion.titulo} - Completado: {self.completado}"

class ProgresoActividad(models.Model):
    id_progreso_actividad = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE)
    puntuacion = models.IntegerField(blank=True, null=True)
    intentos = models.IntegerField(default=0)
    completado = models.BooleanField(default=False) # True si la actividad fue resuelta correctamente
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_ultimo_intento = models.DateTimeField(auto_now=True) # Actualiza cada vez que se guarda
    fecha_completado = models.DateTimeField(blank=True, null=True) # Cuando se obtuvo la puntuación correcta
    puntos_otorgados = models.BooleanField(default=False)

    class Meta:
        unique_together = ('usuario', 'actividad') # Un solo registro por usuario/actividad

    def __str__(self):
        return f"Progreso de {self.usuario.username} en Actividad: {self.actividad.pregunta[:20]}... - Puntos: {self.puntuacion}"