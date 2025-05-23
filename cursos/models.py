# cursos/models.py
from django.db import models
from django.contrib.auth.models import User

class Curso(models.Model):
    id_curso = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    nivel = models.CharField(max_length=50) # Ej: Básico, Intermedio, Avanzado
    imagen_url = models.URLField(max_length=500, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Modulo(models.Model): # <--- ¡Este es el modelo Modulo!
    id_modulo = models.AutoField(primary_key=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='modulos')
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    orden = models.IntegerField(default=1)

    class Meta:
        ordering = ['orden']
        unique_together = ('curso', 'orden') # No puede haber dos módulos con el mismo orden en el mismo curso

    def __str__(self):
        return f"{self.nombre} ({self.curso.nombre})"

class Leccion(models.Model):
    id_leccion = models.AutoField(primary_key=True)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='lecciones') # Relación con Modulo
    titulo = models.CharField(max_length=255)
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
    tipo_actividad = models.CharField(max_length=100) # Ej: 'opcion_multiple', 'arrastrar_soltar', 'respuesta_abierta'
    pregunta = models.TextField()
    opciones = models.JSONField(blank=True, null=True) # Para opciones de opción múltiple, etc.
    respuesta_correcta = models.TextField(blank=True, null=True)
    puntos = models.IntegerField(default=10)

    def __str__(self):
        return f"Actividad {self.id_actividad} - {self.tipo_actividad} de {self.leccion.titulo}"

class ProgresoUsuario(models.Model):
    id_progreso = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, blank=True, null=True)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, blank=True, null=True)
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE, blank=True, null=True)
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, blank=True, null=True)
    completado = models.BooleanField(default=False)
    fecha_completado = models.DateTimeField(blank=True, null=True)
    puntos_ganados = models.IntegerField(default=0)

    class Meta:
        # Esto podría necesitar ajustarse según tu lógica de negocio
        # Si un usuario puede tener progreso en múltiples elementos
        pass

    def __str__(self):
        item_nombre = "N/A"
        if self.curso:
            item_nombre = self.curso.nombre
        elif self.modulo:
            item_nombre = self.modulo.nombre
        elif self.leccion:
            item_nombre = self.leccion.titulo
        elif self.actividad:
            item_nombre = self.actividad.pregunta[:20] + "..."
        return f"Progreso de {self.usuario.username} en {item_nombre} - Completado: {self.completado}"