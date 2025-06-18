# cursos/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction # Importar transaction para atomicidad
import logging

# Importa solo los modelos de cursos y progreso necesarios para la propagación
from .models import ProgresoActividad, ProgresoLeccion, ProgresoModulo, ProgresoCurso, Actividad, Leccion, Modulo, Curso

logger = logging.getLogger(__name__)

# --- Señales para la Propagación de Progreso ---

@receiver(post_save, sender=ProgresoActividad)
def verificar_y_actualizar_progreso_leccion(sender, instance, created, **kwargs):
    """
    Se dispara cuando un ProgresoActividad se guarda.
    Verifica si todas las actividades de una lección están completadas por el usuario
    y actualiza el ProgresoLeccion correspondiente.
    """
    # Solo actuar si el progreso de la actividad ha sido marcado como completado
    # y no es una creación inicial (cuando 'completado' es False por defecto)
    if instance.completado and not created:
        usuario = instance.usuario
        leccion = instance.actividad.leccion
        logger.debug(f"DEBUG: Revisando progreso de lección para {usuario.username} en {leccion.titulo}...")

        # Contar actividades completadas para esta lección y usuario
        actividades_totales = Actividad.objects.filter(leccion=leccion).count()
        actividades_completadas_usuario = ProgresoActividad.objects.filter(
            usuario=usuario,
            actividad__leccion=leccion,
            completado=True
        ).count()

        logger.debug(f"DEBUG: Actividades completadas en lección '{leccion.titulo}': {actividades_completadas_usuario}/{actividades_totales}")

        if actividades_totales > 0 and actividades_completadas_usuario == actividades_totales:
            # Todas las actividades de la lección están completadas
            progreso_leccion, created_leccion = ProgresoLeccion.objects.get_or_create(
                usuario=usuario,
                leccion=leccion
            )
            if not progreso_leccion.completado: # Solo actualizar si no estaba completado
                progreso_leccion.completado = True
                progreso_leccion.fecha_completado = timezone.now()
                progreso_leccion.save(update_fields=['completado', 'fecha_completado']) # Guardar solo los campos modificados
                logger.info(f"INFO: Progreso de lección '{leccion.titulo}' completado automáticamente para {usuario.username}.")
            else:
                logger.debug(f"DEBUG: ProgresoLeccion '{leccion.titulo}' ya estaba completo para {usuario.username}. No se guardó de nuevo.")
        else:
            logger.debug(f"DEBUG: Lección '{leccion.titulo}' no completada aún por actividades para {usuario.username}. Completadas: {actividades_completadas_usuario}/{actividades_totales}")


@receiver(post_save, sender=ProgresoLeccion)
def verificar_y_actualizar_progreso_modulo(sender, instance, created, **kwargs):
    """
    Se dispara cuando un ProgresoLeccion se guarda.
    Verifica si todas las lecciones de un módulo están completadas por el usuario
    y actualiza el ProgresoModulo correspondiente.
    """
    if instance.completado and not created:
        usuario = instance.usuario
        modulo = instance.leccion.modulo
        logger.debug(f"DEBUG: Revisando progreso de módulo para {usuario.username} en {modulo.nombre}...")

        lecciones_totales = Leccion.objects.filter(modulo=modulo).count()
        lecciones_completadas_usuario = ProgresoLeccion.objects.filter(
            usuario=usuario,
            leccion__modulo=modulo,
            completado=True
        ).count()

        logger.debug(f"DEBUG: Lecciones completadas en módulo '{modulo.nombre}': {lecciones_completadas_usuario}/{lecciones_totales}")

        if lecciones_totales > 0 and lecciones_completadas_usuario == lecciones_totales:
            progreso_modulo, created_modulo = ProgresoModulo.objects.get_or_create(
                usuario=usuario,
                modulo=modulo
            )
            if not progreso_modulo.completado:
                progreso_modulo.completado = True
                progreso_modulo.fecha_completado = timezone.now()
                progreso_modulo.save(update_fields=['completado', 'fecha_completado'])
                logger.info(f"INFO: Progreso de módulo '{modulo.nombre}' completado automáticamente para {usuario.username}.")
            else:
                logger.debug(f"DEBUG: ProgresoModulo '{modulo.nombre}' ya estaba completo para {usuario.username}. No se guardó de nuevo.")
        else:
            logger.debug(f"DEBUG: Módulo '{modulo.nombre}' no completado aún por lecciones para {usuario.username}. Completadas: {lecciones_completadas_usuario}/{lecciones_totales}")


@receiver(post_save, sender=ProgresoModulo)
def verificar_y_actualizar_progreso_curso(sender, instance, created, **kwargs):
    """
    Se dispara cuando un ProgresoModulo se guarda.
    Verifica si todos los módulos de un curso están completados por el usuario
    y actualiza el ProgresoCurso correspondiente.
    """
    if instance.completado and not created:
        usuario = instance.usuario
        curso = instance.modulo.curso
        logger.debug(f"DEBUG: Revisando progreso de curso para {usuario.username} en {curso.nombre}...")

        modulos_totales = Modulo.objects.filter(curso=curso).count()
        modulos_completados_usuario = ProgresoModulo.objects.filter(
            usuario=usuario,
            modulo__curso=curso,
            completado=True
        ).count()

        logger.debug(f"DEBUG: Módulos completados en curso '{curso.nombre}': {modulos_completados_usuario}/{modulos_totales}")

        if modulos_totales > 0 and modulos_completados_usuario == modulos_totales:
            progreso_curso, created_curso = ProgresoCurso.objects.get_or_create(
                usuario=usuario,
                curso=curso
            )
            if not progreso_curso.completado:
                progreso_curso.completado = True
                progreso_curso.fecha_completado = timezone.now()
                progreso_curso.save(update_fields=['completado', 'fecha_completado'])
                logger.info(f"INFO: Progreso de curso '{curso.nombre}' completado automáticamente para {usuario.username}.")
            else:
                logger.debug(f"DEBUG: ProgresoCurso '{curso.nombre}' ya estaba completo para {usuario.username}. No se guardó de nuevo.")
        else:
            logger.debug(f"DEBUG: Curso '{curso.nombre}' no completado aún por módulos para {usuario.username}. Completadas: {modulos_completados_usuario}/{modulos_totales}")