# cursos/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import ProgresoLeccion, ProgresoModulo, ProgresoCurso, Leccion, Modulo, Curso, Actividad, ProgresoActividad
from django.contrib.auth.models import User
from django.db.models import Count
import logging 

logger = logging.getLogger(__name__) 

@receiver(post_save, sender=ProgresoActividad)
def actualizar_progreso_leccion_desde_actividad(sender, instance, created, **kwargs):
    logger.debug("DEBUG: Señal de ProgresoActividad disparada.")
    """
    Actualiza el ProgresoLeccion cuando un ProgresoActividad se completa.
    """
    # Nos aseguramos de que solo actuamos cuando la actividad se ha marcado como completada
    # y no es una creación inicial de un progreso (que no debería estar completado al inicio).
    if instance.completado and not created: 
        usuario = instance.usuario
        actividad = instance.actividad
        leccion = actividad.leccion

        # Contar actividades completadas en la lección
        actividades_de_la_leccion = Actividad.objects.filter(leccion=leccion).count()
        actividades_completadas = ProgresoActividad.objects.filter(
            usuario=usuario,
            actividad__leccion=leccion,
            completado=True
        ).count()

        logger.debug(f"DEBUG: Actividades completadas para {leccion.titulo}: {actividades_completadas}/{actividades_de_la_leccion} por {usuario.username}")


        if actividades_de_la_leccion > 0 and actividades_completadas == actividades_de_la_leccion:
            # Todas las actividades de la lección están completadas, marcar la lección
            progreso_leccion, created_pl = ProgresoLeccion.objects.get_or_create(
                usuario=usuario,
                leccion=leccion
            )
            # Solo si el progreso de la lección no estaba ya completado
            if not progreso_leccion.completado:
                progreso_leccion.completado = True
                progreso_leccion.fecha_completado = timezone.now()
                progreso_leccion.save(update_fields=['completado', 'fecha_completado'])
                logger.info(f"INFO: Lección '{leccion.titulo}' completada automáticamente por actividades para {usuario.username}")
            else:
                logger.debug(f"DEBUG: ProgresoLeccion '{leccion.titulo}' ya estaba completo para {usuario.username}. No se guardó de nuevo.")
        else:
            logger.debug(f"DEBUG: Lección '{leccion.titulo}' no completada aún por actividades para {usuario.username}.")


@receiver(post_save, sender=ProgresoLeccion)
def actualizar_progreso_modulo_desde_leccion(sender, instance, created, **kwargs): # Renombrada para claridad
    """
    Actualiza el ProgresoModulo cuando un ProgresoLeccion se completa.
    """
    if instance.completado and not created:
        usuario = instance.usuario
        leccion = instance.leccion
        modulo = leccion.modulo

        # Contar lecciones completadas en el módulo
        lecciones_del_modulo = Leccion.objects.filter(modulo=modulo).count()
        lecciones_completadas = ProgresoLeccion.objects.filter(
            usuario=usuario,
            leccion__modulo=modulo,
            completado=True
        ).count()

        logger.debug(f"DEBUG: Lecciones completadas para {modulo.nombre}: {lecciones_completadas}/{lecciones_del_modulo} por {usuario.username}")

        if lecciones_del_modulo > 0 and lecciones_completadas == lecciones_del_modulo:
            progreso_modulo, created_pm = ProgresoModulo.objects.get_or_create(
                usuario=usuario,
                modulo=modulo
            )
            if not progreso_modulo.completado:
                progreso_modulo.completado = True
                progreso_modulo.fecha_completado = timezone.now()
                progreso_modulo.save(update_fields=['completado', 'fecha_completado'])
                logger.info(f"INFO: Módulo '{modulo.nombre}' completado automáticamente por lecciones para {usuario.username}")
            else:
                logger.debug(f"DEBUG: ProgresoModulo '{modulo.nombre}' ya estaba completo para {usuario.username}. No se guardó de nuevo.")
        else:
            logger.debug(f"DEBUG: Módulo '{modulo.nombre}' no completado aún por lecciones para {usuario.username}.")


@receiver(post_save, sender=ProgresoModulo)
def actualizar_progreso_curso_desde_modulo(sender, instance, created, **kwargs): # Renombrada para claridad
    """
    Actualiza el ProgresoCurso cuando un ProgresoModulo se completa.
    """
    if instance.completado and not created:
        usuario = instance.usuario
        modulo = instance.modulo
        curso = modulo.curso

        # Contar módulos completados en el curso
        modulos_del_curso = Modulo.objects.filter(curso=curso).count()
        modulos_completados = ProgresoModulo.objects.filter(
            usuario=usuario,
            modulo__curso=curso,
            completado=True
        ).count()

        logger.debug(f"DEBUG: Módulos completados para {curso.nombre}: {modulos_completados}/{modulos_del_curso} por {usuario.username}")

        if modulos_del_curso > 0 and modulos_completados == modulos_del_curso:
            progreso_curso, created_pc = ProgresoCurso.objects.get_or_create(
                usuario=usuario,
                curso=curso
            )
            if not progreso_curso.completado:
                progreso_curso.completado = True
                progreso_curso.fecha_completado = timezone.now()
                progreso_curso.save(update_fields=['completado', 'fecha_completado'])
                logger.info(f"INFO: Curso '{curso.nombre}' completado automáticamente por módulos para {usuario.username}")
            else:
                logger.debug(f"DEBUG: ProgresoCurso '{curso.nombre}' ya estaba completo para {usuario.username}. No se guardó de nuevo.")
        else:
            logger.debug(f"DEBUG: Curso '{curso.nombre}' no completado aún por módulos para {usuario.username}.")

# La función auxiliar _actualizar_progreso_curso_desde_modulo
# Ya no es necesaria como una función independiente llamada desde otra señal.
# La señal @receiver(post_save, sender=ProgresoModulo) actualizada ahora maneja esto directamente.
# Puedes eliminar esta función o mantenerla como referencia, pero no será usada activamente.
# def _actualizar_progreso_curso_desde_modulo(usuario, curso):
#     # ... tu código actual de esta función ...
#     pass