# gamificacion/models.py
from django.db import models
from django.contrib.auth.models import User # Para el usuario

class Logro(models.Model):
    id_logro = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField()
    imagen_url = models.URLField(max_length=500, blank=True, null=True) # Imagen del distintivo
    # Puedes añadir un campo para el criterio del logro, ej:
    # tipo_criterio = models.CharField(max_length=100, default='completar_lecciones')
    # valor_criterio = models.IntegerField(default=1) # ej. 10 lecciones, 1 curso

    def __str__(self):
        return self.nombre

class LogroUsuario(models.Model): # Tabla de unión para logros_usuario
    id_logro_usuario = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    logro = models.ForeignKey(Logro, on_delete=models.CASCADE)
    fecha_obtenido = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'logro') # Un usuario solo puede obtener un logro una vez

    def __str__(self):
        return f"{self.usuario.username} obtuvo {self.logro.nombre}"