# gamificacion/signals.py (Reemplaza el contenido completo con esto)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction  # Para asegurar atomicidad en ciertas operaciones
import logging

from .models import PuntosUsuario, Nivel, Insignia, InsigniaUsuario
from cursos.models import (
    ProgresoActividad,
    ProgresoLeccion,
    ProgresoModulo,
    Curso,
    ProgresoCurso,
)  # Importamos Curso para el gestor de insignias

logger = logging.getLogger(__name__)

# --- Constantes de Puntos y Nombres de Insignias ---
PUNTOS_POR_ACTIVIDAD = 5
PUNTOS_POR_LECCION = 10
PUNTOS_POR_MODULO = 20
PUNTOS_POR_CURSO = 50
PUNTOS_POR_LOGIN_DIARIO = 5  # Definido aquí para consistencia

INSIGNIA_PRIMERA_ACTIVIDAD_COMPLETADA = 'Primeros Pasos (Actividad)'
INSIGNIA_PRIMERA_LECCION_COMPLETADA = 'Aprendiz (Lección)'
INSIGNIA_PRIMER_MODULO_COMPLETADO = 'Explorador (Módulo)'
INSIGNIA_PRIMER_CURSO_COMPLETADO = 'Maestro (Curso)'
INSIGNIA_DEDICACION = 'Dedicación'  # Asumiendo un nombre para esta insignia

# --- NUEVA: Insignias de Criterio Complejo ---
INSIGNIA_COMPLETO_3_CURSOS = 'Coleccionista de Cursos'
INSIGNIA_TODO_BASICO = 'Dominador Básico'


# --- Funciones auxiliares para la lógica de Gamificación ---


def otorgar_insignia(usuario, nombre_insignia):
  """
    Función auxiliar para otorgar una insignia.
    Retorna True si la insignia fue otorgada, False si ya la tenía o si no existe.
    """
  try:
    insignia = Insignia.objects.get(nombre=nombre_insignia)
    # Usar get_or_create para evitar duplicados y ser idempotente
    insignia_usuario, created = InsigniaUsuario.objects.get_or_create(
        usuario=usuario, insignia=insignia
    )
    if created:
      logger.debug(
          f"DEBUG: Insignia '{nombre_insignia}' otorgada a {usuario.username}."
      )
      return True
    else:
      logger.debug(
          f"DEBUG: {usuario.username} ya tiene la insignia '{nombre_insignia}'."
      )
      return False
  except Insignia.DoesNotExist:
    logger.error(
        f"ERROR: La insignia '{nombre_insignia}' no existe. Creala en el admin y asegúrate de su tipo."
    )
    return False


def asignar_nivel_y_otorgar_insignias_por_puntos(
    usuario, puntos_usuario_instance
):
  """
    Asigna el nivel al usuario basado en sus puntos y otorga insignias basadas en puntos totales.
    """
  # Asignar nivel basado en puntos
  nuevo_nivel = Nivel.objects.filter(
      puntos_minimos__lte=puntos_usuario_instance.puntos
  ).order_by('-puntos_minimos').first()
  if nuevo_nivel and nuevo_nivel != puntos_usuario_instance.nivel_actual:
    puntos_usuario_instance.nivel_actual = nuevo_nivel
    puntos_usuario_instance.save(update_fields=['nivel_actual'])
    logger.debug(
        f'DEBUG {usuario.username} ha alcanzado el nivel: {nuevo_nivel.nombre}'
    )

  # Otorgar insignias basadas en puntos totales (buscando insignias de tipo 'puntos')
  # Este bucle es más genérico para insignias de tipo 'puntos'
  insignias_por_puntos = Insignia.objects.filter(
      tipo_desbloqueo=Insignia.TIPO_PUNTOS,
      puntos_requeridos__lte=puntos_usuario_instance.puntos,
  ).exclude(
      usuarios_con_insignia__usuario=usuario
  )  # Excluir las que ya tiene el usuario

  for insignia in insignias_por_puntos:
    otorgar_insignia(usuario, insignia.nombre)


def gestionar_insignias_complejas(usuario):
  """
    Función que verifica y otorga insignias basadas en criterios complejos.
    Debe llamarse cuando ocurra un evento relevante (ej. completar un curso, etc.).
    """
  # Insignia: "Coleccionista de Cursos" (Completar 3 cursos)
  cursos_completados_count = ProgresoCurso.objects.filter(
      usuario=usuario, completado=True
  ).count()
  if cursos_completados_count >= 3:
    otorgar_insignia(usuario, INSIGNIA_COMPLETO_3_CURSOS)

  # Insignia: "Dominador Básico" (Completar todos los cursos de nivel 'Básico')
  # Obtener IDs de todos los cursos 'Básicos'
  cursos_basicos_ids = list(
      Curso.objects.filter(nivel='Básico').values_list('id', flat=True)
  )
  # Obtener IDs de los cursos 'Básicos' completados por el usuario
  cursos_basicos_completados_ids = list(
      ProgresoCurso.objects.filter(
          usuario=usuario, completado=True, curso__nivel='Básico'  # Asegúrate que tu modelo Curso tenga un campo 'nivel'
      ).values_list('curso_id', flat=True)
  )

  if cursos_basicos_ids and set(cursos_basicos_ids) == set(
      cursos_basicos_completados_ids
  ):
    otorgar_insignia(usuario, INSIGNIA_TODO_BASICO)

  # Puedes añadir más lógica para otras insignias complejas aquí


# --- Señales para Gamificación ---


@receiver(post_save, sender=PuntosUsuario)
def puntos_usuario_post_save(sender, instance, created, **kwargs):
  """
    Señal que se dispara al guardar PuntosUsuario.
    Maneja la asignación de niveles y el otorgamiento de insignias por puntos.
    """
  asignar_nivel_y_otorgar_insignias_por_puntos(instance.usuario, instance)


@receiver(post_save, sender=ProgresoActividad)
def manejar_progreso_actividad_gamificacion(sender, instance, created, **kwargs):
  """
    Maneja la lógica de gamificación cuando se completa un ProgresoActividad.
    Otorga puntos y la insignia de primera actividad completada.
    """
  if instance.completado and not instance.puntos_otorgados:
    with transaction.atomic():
      puntos_usuario = PuntosUsuario.objects.select_for_update().get(
          usuario=instance.usuario
      )
      puntos_usuario.puntos += PUNTOS_POR_ACTIVIDAD
      puntos_usuario.save()  # Esto disparará la señal puntos_usuario_post_save

      instance.puntos_otorgados = True
      instance.save(update_fields=['puntos_otorgados'])
      logger.debug(
          f'DEBUG: Señal gamificación: ProgresoActividad completado para {instance.usuario.username}.'
      )
      logger.debug(
          f'DEBUG: {PUNTOS_POR_ACTIVIDAD} puntos añadidos. Total: {puntos_usuario.puntos}'
      )

      # Otorgar insignia de acción específica
      otorgar_insignia(instance.usuario, INSIGNIA_PRIMERA_ACTIVIDAD_COMPLETADA)


@receiver(post_save, sender=ProgresoLeccion)
def manejar_progreso_leccion_gamificacion(sender, instance, created, **kwargs):
  """
    Maneja la lógica de gamificación cuando se completa un ProgresoLeccion.
    Otorga puntos y la insignia de primera lección completada.
    """
  if instance.completado and not instance.puntos_otorgados:
    with transaction.atomic():
      puntos_usuario = PuntosUsuario.objects.select_for_update().get(
          usuario=instance.usuario
      )
      puntos_usuario.puntos += PUNTOS_POR_LECCION
      puntos_usuario.save()  # Esto disparará la señal puntos_usuario_post_save

      instance.puntos_otorgados = True
      instance.save(update_fields=['puntos_otorgados'])
      logger.debug(
          f'DEBUG: Señal gamificación: ProgresoLeccion completado para {instance.usuario.username}.'
      )
      logger.debug(
          f'DEBUG: {PUNTOS_POR_LECCION} puntos añadidos. Total: {puntos_usuario.puntos}'
      )

      # Otorgar insignia de acción específica
      otorgar_insignia(instance.usuario, INSIGNIA_PRIMERA_LECCION_COMPLETADA)


@receiver(post_save, sender=ProgresoModulo)
def manejar_progreso_modulo_gamificacion(sender, instance, created, **kwargs):
  """
    Maneja la lógica de gamificación cuando se completa un ProgresoModulo.
    Otorga puntos y la insignia de primer módulo completado.
    """
  if instance.completado and not instance.puntos_otorgados:
    with transaction.atomic():
      puntos_usuario = PuntosUsuario.objects.select_for_update().get(
          usuario=instance.usuario
      )
      puntos_usuario.puntos += PUNTOS_POR_MODULO
      puntos_usuario.save()  # Esto disparará la señal puntos_usuario_post_save

      instance.puntos_otorgados = True
      instance.save(update_fields=['puntos_otorgados'])
      logger.debug(
          f'DEBUG: Señal gamificación: ProgresoModulo completado para {instance.usuario.username}.'
      )
      logger.debug(
          f'DEBUG: {PUNTOS_POR_MODULO} puntos añadidos. Total: {puntos_usuario.puntos}'
      )

      # Otorgar insignia de acción específica
      otorgar_insignia(instance.usuario, INSIGNIA_PRIMER_MODULO_COMPLETADO)


@receiver(post_save, sender=ProgresoCurso)
def manejar_progreso_curso_gamificacion(sender, instance, created, **kwargs):
  """
    Maneja la lógica de gamificación cuando se completa un ProgresoCurso.
    Otorga puntos, la insignia de primer curso completado y
    llama al gestor de insignias complejas.
    """
  if instance.completado and not instance.puntos_otorgados:
    with transaction.atomic():
      puntos_usuario = PuntosUsuario.objects.select_for_update().get(
          usuario=instance.usuario
      )
      puntos_usuario.puntos += PUNTOS_POR_CURSO
      puntos_usuario.save()  # Esto disparará la señal puntos_usuario_post_save

      instance.puntos_otorgados = True
      instance.save(update_fields=['puntos_otorgados'])
      logger.debug(
          f'DEBUG: Señal gamificación: ProgresoCurso completado para {instance.usuario.username}.'
      )
      logger.debug(
          f'DEBUG: {PUNTOS_POR_CURSO} puntos añadidos. Total: {puntos_usuario.puntos}'
      )

      # Otorgar insignia de acción específica
      otorgar_insignia(instance.usuario, INSIGNIA_PRIMER_CURSO_COMPLETADO)

      # Llamar al gestor de insignias complejas después de completar un curso
      gestionar_insignias_complejas(instance.usuario)