from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
import logging
from datetime import timedelta

from django.contrib.auth.signals import user_logged_in  # <-- NUEVO: Para puntos por login

from .models import PuntosUsuario, Nivel, Insignia, InsigniaUsuario
from cursos.models import (
    ProgresoActividad,
    ProgresoLeccion,
    ProgresoModulo,
    Curso,
    ProgresoCurso,
)

logger = logging.getLogger(__name__)

# --- Constantes de Puntos y Nombres de Insignias ---
PUNTOS_POR_ACTIVIDAD = 5
PUNTOS_POR_LECCION = 10
PUNTOS_POR_MODULO = 20
PUNTOS_POR_CURSO = 50
PUNTOS_POR_LOGIN_DIARIO = 5
DIAS_CONSECUTIVOS_PARA_DEDICACION = 7

INSIGNIA_PRIMERA_ACTIVIDAD_COMPLETADA = 'Primeros Pasos (Actividad)'
INSIGNIA_PRIMERA_LECCION_COMPLETADA = 'Aprendiz (Lección)'
INSIGNIA_PRIMER_MODULO_COMPLETADO = 'Explorador (Módulo)'
INSIGNIA_PRIMER_CURSO_COMPLETADO = 'Maestro (Curso)'
INSIGNIA_DEDICACION = 'Dedicación'

# --- Insignias de Criterio Complejo ---
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


def gestionar_niveles_e_insignias_por_puntos(usuario, puntos_usuario_instance):
    """
    Gestiona la asignación de niveles y el otorgamiento de insignias
    basadas en los puntos totales del usuario.
    Esta función ahora es llamada por la señal post_save de PuntosUsuario.
    """
    # 1. Asignar Nivel
    old_level = puntos_usuario_instance.nivel_actual
    if level_changed := puntos_usuario_instance.update_nivel_based_on_points():
        logger.debug(f'DEBUG: Nivel de {usuario.username} actualizado a {puntos_usuario_instance.nivel_actual.nombre}')
    # 2. Otorgar Insignias por Puntos
    insignias_por_puntos = Insignia.objects.filter(
        tipo_desbloqueo=Insignia.TIPO_PUNTOS,
        puntos_requeridos__lte=puntos_usuario_instance.puntos,
    ).exclude(
        usuarios_con_insignia__usuario=usuario
    )

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
    cursos_basicos_totales = Curso.objects.filter(nivel='Básico').count()
    cursos_basicos_ids = list(
        Curso.objects.filter(nivel='Básico').values_list('id_curso', flat=True)
    )
    cursos_basicos_completados_ids = list(
        ProgresoCurso.objects.filter(
            usuario=usuario, completado=True, curso__nivel='Básico'
        ).values_list('curso__id_curso', flat=True)
    )

    print(f"DEBUG_DOMINADOR: Cursos Básicos Totales en el sistema (IDs): {cursos_basicos_ids}")
    print(f"DEBUG_DOMINADOR: Cursos Básicos Completados por {usuario.username} (IDs): {cursos_basicos_completados_ids}")

    if cursos_basicos_ids and set(cursos_basicos_ids) == set(cursos_basicos_completados_ids) and cursos_basicos_totales > 0:
        otorgar_insignia(usuario, INSIGNIA_TODO_BASICO)
        print(f"DEBUG: Insignia '{INSIGNIA_TODO_BASICO}' otorgada a {usuario.username}.")
    else:
        print("DEBUG_DOMINADOR: Condición para Dominador Básico NO cumplida. ")
        print(f"DEBUG_DOMINADOR: IDs Totales: {cursos_basicos_ids}, IDs Completados: {cursos_basicos_completados_ids}")


# --- Señales para Gamificación ---

# Señal PRINCIPAL para PuntosUsuario y Nivel/Insignias por Puntos
@receiver(post_save, sender=PuntosUsuario)
def puntos_usuario_post_save(sender, instance, created, **kwargs):
    """
    Señal que se dispara al guardar PuntosUsuario.
    Maneja la asignación de niveles y el otorgamiento de insignias por puntos.
    """
    with transaction.atomic():
        gestionar_niveles_e_insignias_por_puntos(instance.usuario, instance)
        # Importante: Si el nivel_actual de la instancia se actualizó dentro de
        # gestionar_niveles_e_insignias_por_puntos, el cambio ya está en la instancia
        # en memoria. Aquí podríamos guardar explícitamente si es necesario,
        # pero para evitar bucles si otros post_save también guardan, a veces se prefiere
        # que solo el trigger original de `save()` dispare el post_save.
        # Sin embargo, si `update_nivel_based_on_points` en el modelo no llama a save(),
        # entonces *debemos* guardar aquí si el nivel_actual cambió.
        # La solución más robusta y sin riesgo de recursión es:
        if kwargs.get('update_fields') is None or 'nivel_actual' not in kwargs.get('update_fields', []):
            # Si el save original no incluyó 'nivel_actual' y el nivel cambió,
            # lo guardamos aquí para persistir el cambio.
            # Se usa `update_fields` para especificar solo el campo cambiado
            # y evitar disparar el post_save para otros cambios que no sean el nivel.
            old_nivel = Nivel.objects.filter(usuarios_en_nivel=instance).first() # Obtener nivel ANTES del cambio
            instance.update_nivel_based_on_points() # Re-calcular/setear el nivel en la instancia
            if instance.nivel_actual != old_nivel: # Si realmente cambió
                # Desconectar temporalmente la señal para evitar un bucle infinito
                post_save.disconnect(puntos_usuario_post_save, sender=PuntosUsuario)
                instance.save(update_fields=['nivel_actual'])
                post_save.connect(puntos_usuario_post_save, sender=PuntosUsuario)


# Señal para Puntos por Login Diario
from django.contrib.auth.signals import user_logged_in # <-- Asegúrate de que este import esté AQUÍ (o al principio)

@receiver(user_logged_in)
def otorgar_puntos_por_login_diario(sender, request, user, **kwargs):
    """
    Otorga puntos al usuario una vez al día por iniciar sesión y gestiona la racha de login
    y la insignia de Dedicación.
    """
    with transaction.atomic():
        puntos_usuario, created = PuntosUsuario.objects.get_or_create(usuario=user)
        # select_for_update para asegurar atomicidad si hay concurrencia
        puntos_usuario = PuntosUsuario.objects.select_for_update().get(usuario=user)
        today = timezone.localdate()

        # Si el usuario NO ha recibido puntos hoy
        if puntos_usuario.last_daily_login_award is None or puntos_usuario.last_daily_login_award < today:
            puntos_usuario.puntos += PUNTOS_POR_LOGIN_DIARIO
            logger.debug(
                f"DEBUG: Puntos por login diario: {PUNTOS_POR_LOGIN_DIARIO} puntos añadidos a {user.username}. Total: {puntos_usuario.puntos}"
            )

            # --- Lógica de la racha de login ---
            # Si el último award fue AYER, incrementa la racha
            if puntos_usuario.last_daily_login_award == today - timedelta(days=1):
                puntos_usuario.login_streak += 1
                logger.debug(f"DEBUG: {user.username} ha incrementado su racha a {puntos_usuario.login_streak} días.")
            # Si el último award no fue ayer (o es la primera vez), reinicia la racha a 1
            else:
                if puntos_usuario.login_streak > 0: # Solo si ya tenía una racha y se rompió
                    logger.debug(f"DEBUG: La racha de login de {user.username} se rompió. Racha anterior: {puntos_usuario.login_streak}. Reiniciando a 1.")
                puntos_usuario.login_streak = 1


            puntos_usuario.last_daily_login_award = today
            # Guardar aquí disparará la señal puntos_usuario_post_save
            puntos_usuario.save(update_fields=['puntos', 'last_daily_login_award', 'login_streak'])


            # --- Lógica para la insignia de Dedicación ---
            # Otorga la insignia si la racha alcanza el umbral
            if puntos_usuario.login_streak >= DIAS_CONSECUTIVOS_PARA_DEDICACION:
                otorgar_insignia(user, INSIGNIA_DEDICACION)

        else:
            logger.debug(f"DEBUG: {user.username} ya ha recibido puntos de login diario hoy.")


@receiver(post_save, sender=ProgresoActividad)
def manejar_progreso_actividad_gamificacion(sender, instance, created, **kwargs):
    if instance.completado and not instance.puntos_otorgados:
        with transaction.atomic():
            puntos_usuario = PuntosUsuario.objects.select_for_update().get(
                usuario=instance.usuario
            )
            puntos_usuario.puntos += PUNTOS_POR_ACTIVIDAD
            puntos_usuario.save() # Esto disparará la señal puntos_usuario_post_save

            instance.puntos_otorgados = True
            instance.save(update_fields=['puntos_otorgados'])
            logger.debug(
                f'DEBUG: Señal gamificación: ProgresoActividad completado para {instance.usuario.username}.'
            )
            logger.debug(
                f'DEBUG: {PUNTOS_POR_ACTIVIDAD} puntos añadidos. Total: {puntos_usuario.puntos}'
            )
            otorgar_insignia(instance.usuario, INSIGNIA_PRIMERA_ACTIVIDAD_COMPLETADA)


@receiver(post_save, sender=ProgresoLeccion)
def manejar_progreso_leccion_gamificacion(sender, instance, created, **kwargs):
    if instance.completado and not instance.puntos_otorgados:
        with transaction.atomic():
            puntos_usuario = PuntosUsuario.objects.select_for_update().get(
                usuario=instance.usuario
            )
            puntos_usuario.puntos += PUNTOS_POR_LECCION
            puntos_usuario.save() # Esto disparará la señal puntos_usuario_post_save

            instance.puntos_otorgados = True
            instance.save(update_fields=['puntos_otorgados'])
            logger.debug(
                f'DEBUG: Señal gamificación: ProgresoLeccion completado para {instance.usuario.username}.'
            )
            logger.debug(
                f'DEBUG: {PUNTOS_POR_LECCION} puntos añadidos. Total: {puntos_usuario.puntos}'
            )
            otorgar_insignia(instance.usuario, INSIGNIA_PRIMERA_LECCION_COMPLETADA)


@receiver(post_save, sender=ProgresoModulo)
def manejar_progreso_modulo_gamificacion(sender, instance, created, **kwargs):
    if instance.completado and not instance.puntos_otorgados:
        with transaction.atomic():
            puntos_usuario = PuntosUsuario.objects.select_for_update().get(
                usuario=instance.usuario
            )
            puntos_usuario.puntos += PUNTOS_POR_MODULO
            puntos_usuario.save() # Esto disparará la señal puntos_usuario_post_save

            instance.puntos_otorgados = True
            instance.save(update_fields=['puntos_otorgados'])
            logger.debug(
                f'DEBUG: Señal gamificación: ProgresoModulo completado para {instance.usuario.username}.'
            )
            logger.debug(
                f'DEBUG: {PUNTOS_POR_MODULO} puntos añadidos. Total: {puntos_usuario.puntos}'
            )
            otorgar_insignia(instance.usuario, INSIGNIA_PRIMER_MODULO_COMPLETADO)


@receiver(post_save, sender=ProgresoCurso)
def manejar_progreso_curso_gamificacion(sender, instance, created, **kwargs):
    if instance.completado and not instance.puntos_otorgados:
        with transaction.atomic():
            puntos_usuario = PuntosUsuario.objects.select_for_update().get(
                usuario=instance.usuario
            )
            puntos_usuario.puntos += PUNTOS_POR_CURSO
            puntos_usuario.save() # Esto disparará la señal puntos_usuario_post_save

            instance.puntos_otorgados = True
            instance.save(update_fields=['puntos_otorgados'])
            logger.debug(
                f'DEBUG: Señal gamificación: ProgresoCurso completado para {instance.usuario.username}.'
            )
            logger.debug(
                f'DEBUG: {PUNTOS_POR_CURSO} puntos añadidos. Total: {puntos_usuario.puntos}'
            )

            otorgar_insignia(instance.usuario, INSIGNIA_PRIMER_CURSO_COMPLETADO)
            gestionar_insignias_complejas(instance.usuario)