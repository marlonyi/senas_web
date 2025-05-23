# comunidad/models.py
from django.db import models
from django.conf import settings # Para User model

class Foro(models.Model):
    titulo = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='foros_creados')
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Foros"
        ordering = ['-fecha_creacion'] # Ordenar por fecha de creación descendente

    def __str__(self):
        return self.titulo

class Comentario(models.Model):
    foro = models.ForeignKey(Foro, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comentarios_escritos')
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    # Para comentarios anidados (respuestas)
    parent_comentario = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='respuestas')

    class Meta:
        verbose_name_plural = "Comentarios"
        ordering = ['fecha_creacion'] # Ordenar por fecha de creación ascendente

    def __str__(self):
        return f"Comentario de {self.autor.username} en {self.foro.titulo}"

class MeGustaComentario(models.Model):
    comentario = models.ForeignKey(Comentario, on_delete=models.CASCADE, related_name='me_gustas')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='me_gustas_dados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Me Gusta en Comentarios"
        unique_together = ('comentario', 'usuario') # Un usuario solo puede dar un like a un comentario

    def __str__(self):
        return f"{self.usuario.username} le dio Me Gusta a Comentario {self.comentario.id}"