# cursos/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import ProgresoLeccion, ProgresoModulo, ProgresoCurso, Leccion, Modulo, Curso, Actividad, ProgresoActividad
from django.contrib.auth.models import User # Asegúrate de que User esté importado si lo usas directamente en señales


@receiver(post_save, sender=ProgresoLeccion)
def actualizar_progreso_modulo(sender, instance, created, **kwargs):
    print(f"DEBUG: Señal de ProgresoLeccion disparada para {instance.usuario.username} en lección {instance.leccion.titulo}.")
    if instance.completado: # Solo actuamos si la lección se marca como completada
        usuario = instance.usuario
        leccion = instance.leccion
        modulo = leccion.modulo

        # Obtener o crear ProgresoModulo
        progreso_modulo, created_pm = ProgresoModulo.objects.get_or_create(
            usuario=usuario,
            modulo=modulo
        )
        print(f"DEBUG: ProgresoModulo para {modulo.nombre} - Completado: {progreso_modulo.completado}, Creado: {created_pm}")


        # Contar lecciones completadas en el módulo
        lecciones_del_modulo = Leccion.objects.filter(modulo=modulo).count()
        lecciones_completadas = ProgresoLeccion.objects.filter(
            usuario=usuario,
            leccion__modulo=modulo,
            completado=True
        ).count()
        print(f"DEBUG: Lecciones completadas en módulo '{modulo.nombre}': {lecciones_completadas}/{lecciones_del_modulo}")


        # Actualizar estado de completado del módulo
        if lecciones_del_modulo > 0 and lecciones_completadas == lecciones_del_modulo:
            if not progreso_modulo.completado:
                progreso_modulo.completado = True
                progreso_modulo.fecha_completado = timezone.now()
                progreso_modulo.save() # Este save debería disparar _actualizar_progreso_curso_desde_modulo
                print(f"DEBUG: Módulo '{modulo.nombre}' completado para {usuario.username}")
            else:
                print(f"DEBUG: Módulo '{modulo.nombre}' ya estaba completo para {usuario.username}. No se guardó de nuevo.")
        elif created_pm: # Si se acaba de crear y no está completo, guardarlo (ej. solo por fecha_inicio)
            # No necesitamos guardarlo aquí si solo se crea y no se completa,
            # ya que get_or_create ya lo guardó si fue creado.
            # Pero si necesitas una fecha_inicio específica, podrías hacerlo.
            print(f"DEBUG: ProgresoModulo '{modulo.nombre}' creado pero no completado aún para {usuario.username}.")

        # Después de actualizar el progreso del módulo, intentar actualizar el progreso del curso
        # Llamamos a esta función directamente, no esperamos otra señal de save().
        # Es importante no llamar a save() en ProgresoModulo si no hubo un cambio de estado
        # que justifique disparar esta función recursivamente, ya que podría generar un bucle.
        _actualizar_progreso_curso_desde_modulo(usuario, modulo.curso)


@receiver(post_save, sender=ProgresoActividad)
def actualizar_progreso_leccion_desde_actividad(sender, instance, created, **kwargs):
    print("DEBUG: Señal de ProgresoActividad disparada.") # <-- Esta ya la confirmamos
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
                progreso_leccion.save() # <-- ¡Este save debe disparar la señal de ProgresoLeccion!
                print(f"DEBUG: Lección '{leccion.titulo}' completada automáticamente por actividad para {usuario.username}")
            else:
                print(f"DEBUG: ProgresoLeccion '{leccion.titulo}' ya estaba completo para {usuario.username}. No se guardó de nuevo.")
        else:
            print(f"DEBUG: Lección '{leccion.titulo}' no completada aún por actividades para {usuario.username}. Completadas: {actividades_completadas}/{actividades_de_la_leccion}")


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
    print(f"DEBUG: ProgresoCurso para {curso.nombre} - Completado: {progreso_curso.completado}, Creado: {created_pc}")


    # Contar módulos completados en el curso
    modulos_del_curso = Modulo.objects.filter(curso=curso).count()
    modulos_completados = ProgresoModulo.objects.filter(
        usuario=usuario,
        modulo__curso=curso,
        completado=True
    ).count()
    print(f"DEBUG: Módulos completados en curso '{curso.nombre}': {modulos_completados}/{modulos_del_curso}")


    # Actualizar estado de completado del curso
    if modulos_del_curso > 0 and modulos_completados == modulos_del_curso:
        if not progreso_curso.completado:
            progreso_curso.completado = True
            progreso_curso.fecha_completado = timezone.now()
            progreso_curso.save()
            print(f"DEBUG: Curso '{curso.nombre}' completado para {usuario.username}")
        else:
            print(f"DEBUG: Curso '{curso.nombre}' ya estaba completo para {usuario.username}. No se guardó de nuevo.")
    elif created_pc: # Si se acaba de crear y no está completo, guardarlo (ej. solo por fecha_inicio)
        # Similar al ProgresoModulo, get_or_create ya lo guardó si fue creado.
        print(f"DEBUG: ProgresoCurso '{curso.nombre}' creado pero no completado aún para {usuario.username}.")