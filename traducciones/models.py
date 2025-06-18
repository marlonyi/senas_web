# traducciones/models.py
from django.db import models

class CategoriaSenda(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categorías de Sendas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Senda(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField(blank=True, null=True, help_text="Aquí puede ir la descripción de la seña, URL de video, etc.")
    categoria = models.ForeignKey(CategoriaSenda, on_delete=models.SET_NULL, null=True, blank=True, related_name='sendas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Sendas"
        ordering = ['titulo']

    def __str__(self):
        return self.titulo