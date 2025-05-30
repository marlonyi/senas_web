# cursos/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import ProgresoLeccion, ProgresoModulo, ProgresoCurso, Leccion, Modulo, Curso, Actividad, ProgresoActividad
from django.contrib.auth.models import User
from django.db.models import Count
import logging # Importar el módulo de logging

logger = logging.getLogger(__name__) # Inicializar el logger

@receiver(post_save, sender=ProgresoLeccion)
def actualizar_progreso_modulo(sender, instance, created, **kwargs):
    logger.debug(f"DEBUG: Señal de ProgresoLeccion disparada para {instance.usuario.username} en lección {instance.leccion.titulo}.")
    if instance.completado: # Solo actuamos si la lección se marca como completada
        usuario = instance.usuario
        leccion = instance.leccion
        modulo = leccion.modulo

        # Obtener o crear ProgresoModulo
        progreso_modulo, created_pm = ProgresoModulo.objects.get_or_create(
            usuario=usuario,
            modulo=modulo
        )
        logger.debug(f"DEBUG: ProgresoModulo para {modulo.nombre} - Completado: {progreso_modulo.completado}, Creado: {created_pm}")


        # Contar lecciones completadas en el módulo
        lecciones_del_modulo = Leccion.objects.filter(modulo=modulo).count()
        lecciones_completadas = ProgresoLeccion.objects.filter(
            usuario=usuario,
            leccion__modulo=modulo,
            completado=True
        ).count()
        logger.debug(f"DEBUG: Lecciones completadas en módulo '{modulo.nombre}': {lecciones_completadas}/{lecciones_del_modulo}")


        # Actualizar estado de completado del módulo
        if lecciones_del_modulo > 0 and lecciones_completadas == lecciones_del_modulo:
            if not progreso_modulo.completado:
                progreso_modulo.completado = True
                progreso_modulo.fecha_completado = timezone.now()
                # CAMBIO CRUCIAL: Usar update_fields para no sobrescribir puntos_otorgados
                progreso_modulo.save(update_fields=['completado', 'fecha_completado'])
                logger.debug(f"DEBUG: Módulo '{modulo.nombre}' completado para {usuario.username}")
            else:
                logger.debug(f"DEBUG: Módulo '{modulo.nombre}' ya estaba completo para {usuario.username}. No se guardó de nuevo.")
        elif created_pm:
            logger.debug(f"DEBUG: ProgresoModulo '{modulo.nombre}' creado pero no completado aún para {usuario.username}.")

        # Después de actualizar el progreso del módulo, intentar actualizar el progreso del curso
        # Llamamos a esta función directamente, no esperamos otra señal de save().
        _actualizar_progreso_curso_desde_modulo(usuario, modulo.curso)


@receiver(post_save, sender=ProgresoActividad)
def actualizar_progreso_leccion_desde_actividad(sender, instance, created, **kwargs):
    logger.debug("DEBUG: Señal de ProgresoActividad disparada.")
    """
    Actualiza el ProgresoLeccion cuando un ProgresoActividad se completa.
    """
    if instance.completado: # Solo actuamos si la actividad se marca como completada
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

        if actividades_de_la_leccion > 0 and actividades_completadas == actividades_de_la_leccion:
            # Todas las actividades de la lección están completadas, marcar la lección
            progreso_leccion, created_pl = ProgresoLeccion.objects.get_or_create(
                usuario=usuario,
                leccion=leccion
            )
            if not progreso_leccion.completado:
                progreso_leccion.completado = True
                progreso_leccion.fecha_completado = timezone.now()
                # CAMBIO CRUCIAL: Usar update_fields para no sobrescribir puntos_otorgados
                progreso_leccion.save(update_fields=['completado', 'fecha_completado'])
                logger.debug(f"DEBUG: Lección '{leccion.titulo}' completada automáticamente por actividad para {usuario.username}")
            else:
                logger.debug(f"DEBUG: ProgresoLeccion '{leccion.titulo}' ya estaba completo para {usuario.username}. No se guardó de nuevo.")
        else:
            logger.debug(f"DEBUG: Lección '{leccion.titulo}' no completada aún por actividades para {usuario.username}. Completadas: {actividades_completadas}/{actividades_de_la_leccion}")


def _actualizar_progreso_curso_desde_modulo(usuario, curso):
    """
    Función auxiliar para actualizar el ProgresoCurso.
    Se llama desde la señal de ProgresoModulo.
    """
    # Obtener o crear ProgresoCurso
    progreso_curso, created_pc = ProgresoCurso.objects.get_or_create(
        usuario=usuario,
        curso=curso
    )
    logger.debug(f"DEBUG: ProgresoCurso para {curso.nombre} - Completado: {progreso_curso.completado}, Creado: {created_pc}")


    # Contar módulos completados en el curso
    modulos_del_curso = Modulo.objects.filter(curso=curso).count()
    modulos_completados = ProgresoModulo.objects.filter(
        usuario=usuario,
        modulo__curso=curso,
        completado=True
    ).count()
    logger.debug(f"DEBUG: Módulos completados en curso '{curso.nombre}': {modulos_completados}/{modulos_del_curso}")


    # Actualizar estado de completado del curso
    if modulos_del_curso > 0 and modulos_completados == modulos_del_curso:
        if not progreso_curso.completado:
            progreso_curso.completado = True
            progreso_curso.fecha_completado = timezone.now()
            # CAMBIO CRUCIAL: Usar update_fields para no sobrescribir puntos_otorgados
            progreso_curso.save(update_fields=['completado', 'fecha_completado'])
            logger.debug(f"DEBUG: Curso '{curso.nombre}' completado para {usuario.username}")
        else:
            logger.debug(f"DEBUG: Curso '{curso.nombre}' ya estaba completo para {usuario.username}. No se guardó de nuevo.")
    elif created_pc:
        logger.debug(f"DEBUG: ProgresoCurso '{curso.nombre}' creado pero no completado aún para {usuario.username}.")

# --- NUEVA SEÑAL PARA ACTUALIZAR PROGRESO CURSO DESDE MODULO (si no la tenías ya) ---
# Asegúrate de que esta señal se conecte a ProgresoModulo
@receiver(post_save, sender=ProgresoModulo)
def actualizar_progreso_curso(sender, instance, created, **kwargs): # <-- CAMBIO AQUÍ: Renombrada
    # Solo si el módulo se acaba de completar o su estado de completado ha cambiado
    # Nota: instance.tracker.has_changed('completado') requiere django-model-utils FieldTracker.
    # Si no lo tienes instalado/configurado, esta condición no funcionará y deberías quitarla
    # o simplificarla si solo te importa el 'completado' sin tracking de cambios específicos.
    # Para la mayoría de los casos, 'instance.completado and (created or instance.fecha_completado)' podría ser suficiente,
    # o simplemente 'instance.completado'.
    if instance.completado: # Simplificado para evitar dependencia de FieldTracker si no lo tienes
        logger.debug(f"DEBUG: Señal de ProgresoModulo disparada para {instance.usuario.username} en módulo {instance.modulo.nombre}.")
        _actualizar_progreso_curso_desde_modulo(instance.usuario, instance.modulo.curso)
