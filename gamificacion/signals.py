# gamificacion/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Nivel, PuntosUsuario, Insignia, InsigniaUsuario
from cursos.models import ProgresoActividad, ProgresoLeccion, ProgresoModulo, ProgresoCurso # Importa tus modelos de Progreso
import logging

logger = logging.getLogger(__name__) # Configura un logger para depuración

# Define los puntos que se otorgarán
PUNTOS_POR_ACTIVIDAD = 5
PUNTOS_POR_LECCION = 10
PUNTOS_POR_MODULO = 20
PUNTOS_POR_CURSO = 50

# Define los nombres de las insignias (deben coincidir con los nombres que crees en el admin)
INSIGNIA_PRIMERA_ACTIVIDAD_COMPLETADA = "Primeros Pasos (Actividad)"
INSIGNIA_PRIMERA_LECCION_COMPLETADA = "Aprendiz (Lección)"
INSIGNIA_PRIMER_MODULO_COMPLETADO = "Explorador (Módulo)"
INSIGNIA_PRIMER_CURSO_COMPLETADO = "Maestro (Curso)"
INSIGNIA_DEDICACION = "Dedicación (100 Puntos)" # Ejemplo de insignia basada en puntos

def obtener_o_crear_puntos_usuario(user):
    """Helper para obtener o inicializar los puntos de un usuario."""
    puntos_usuario, created = PuntosUsuario.objects.get_or_create(usuario=user)
    if created:
        logger.debug(f"DEBUG: Se crearon PuntosUsuario para {user.username} con 0 puntos.")
    return puntos_usuario

def otorgar_insignia(usuario, nombre_insignia):
    """Helper para otorgar una insignia si no la tiene ya."""
    try:
        insignia = Insignia.objects.get(nombre=nombre_insignia)
        insignia_usuario, created = InsigniaUsuario.objects.get_or_create(
            usuario=usuario,
            insignia=insignia
        )
        if created:
            logger.debug(f"DEBUG: Insignia '{nombre_insignia}' otorgada a {usuario.username}.")
            return True
        else:
            logger.debug(f"DEBUG: {usuario.username} ya tiene la insignia '{nombre_insignia}'.")
            return False
    except Insignia.DoesNotExist:
        logger.error(f"ERROR: La insignia '{nombre_insignia}' no existe. Creala en el admin.")
        return False

# Señal para manejar el progreso de Actividad y otorgar puntos/insignias
@receiver(post_save, sender=ProgresoActividad)
def manejar_progreso_actividad_gamificacion(sender, instance, created, **kwargs):
    # Solo actuar si la actividad está completada y se acaba de completar o ha sido actualizada
    if instance.completado and (created or instance.tracker.has_changed('completado')): # Usar un tracker para solo actuar en el cambio de estado
        logger.debug(f"DEBUG: Señal gamificación: ProgresoActividad completado para {instance.usuario.username}.")
        puntos_usuario = obtener_o_crear_puntos_usuario(instance.usuario)
        
        # Incrementar puntos solo si no los ha recibido ya por esta actividad
        # (Esto asume que el progreso_actividad no debería tener puntos duplicados)
        # Una forma más robusta sería tener un campo 'puntos_otorgados' en ProgresoActividad.
        # Por ahora, simplemente añadimos, pero si hay múltiples saves de la misma actividad, sumará varias veces.
        # Una mejor solución sería:
        # if not hasattr(instance, '_puntos_otorgados_por_actividad'):
        #     puntos_usuario.puntos += PUNTOS_POR_ACTIVIDAD
        #     puntos_usuario.save()
        #     instance._puntos_otorgados_por_actividad = True
        
        # Para evitar sumar puntos multiples veces si se actualiza varias veces la misma actividad completada
        # sin cambiar el estado de completado a falso y luego a verdadero de nuevo.
        # Esto es un placeholder; una solución robusta podría requerir un campo en el modelo de progreso
        # o un chequeo más específico de la última vez que se le dio puntos por esta actividad.
        # Para una prueba simple, esto bastará:
        puntos_usuario.puntos += PUNTOS_POR_ACTIVIDAD
        puntos_usuario.save() # Esto disparará la señal de PuntosUsuario

        logger.debug(f"DEBUG: {PUNTOS_POR_ACTIVIDAD} puntos añadidos. Total: {puntos_usuario.puntos}")

        # Otorgar insignia por primera actividad completada
        # Contamos solo las actividades completadas del usuario. Si es 1, es la primera.
        if ProgresoActividad.objects.filter(usuario=instance.usuario, completado=True).count() == 1:
            otorgar_insignia(instance.usuario, INSIGNIA_PRIMERA_ACTIVIDAD_COMPLETADA)


@receiver(post_save, sender=ProgresoLeccion)
def manejar_progreso_leccion_gamificacion(sender, instance, created, **kwargs):
    if instance.completado and (created or instance.tracker.has_changed('completado')):
        logger.debug(f"DEBUG: Señal gamificación: ProgresoLeccion completado para {instance.usuario.username}.")
        puntos_usuario = obtener_o_crear_puntos_usuario(instance.usuario)
        puntos_usuario.puntos += PUNTOS_POR_LECCION
        puntos_usuario.save() # Esto disparará la señal de PuntosUsuario
        logger.debug(f"DEBUG: {PUNTOS_POR_LECCION} puntos añadidos. Total: {puntos_usuario.puntos}")

        # Otorgar insignia por primera lección completada
        if ProgresoLeccion.objects.filter(usuario=instance.usuario, completado=True).count() == 1:
            otorgar_insignia(instance.usuario, INSIGNIA_PRIMERA_LECCION_COMPLETADA)


@receiver(post_save, sender=ProgresoModulo)
def manejar_progreso_modulo_gamificacion(sender, instance, created, **kwargs):
    if instance.completado and (created or instance.tracker.has_changed('completado')):
        logger.debug(f"DEBUG: Señal gamificación: ProgresoModulo completado para {instance.usuario.username}.")
        puntos_usuario = obtener_o_crear_puntos_usuario(instance.usuario)
        puntos_usuario.puntos += PUNTOS_POR_MODULO
        puntos_usuario.save() # Esto disparará la señal de PuntosUsuario
        logger.debug(f"DEBUG: {PUNTOS_POR_MODULO} puntos añadidos. Total: {puntos_usuario.puntos}")

        # Otorgar insignia por primer módulo completado
        if ProgresoModulo.objects.filter(usuario=instance.usuario, completado=True).count() == 1:
            otorgar_insignia(instance.usuario, INSIGNIA_PRIMER_MODULO_COMPLETADO)

@receiver(post_save, sender=ProgresoCurso)
def manejar_progreso_curso_gamificacion(sender, instance, created, **kwargs):
    if instance.completado and (created or instance.tracker.has_changed('completado')):
        logger.debug(f"DEBUG: Señal gamificación: ProgresoCurso completado para {instance.usuario.username}.")
        puntos_usuario = obtener_o_crear_puntos_usuario(instance.usuario)
        puntos_usuario.puntos += PUNTOS_POR_CURSO
        puntos_usuario.save() # Esto disparará la señal de PuntosUsuario
        logger.debug(f"DEBUG: {PUNTOS_POR_CURSO} puntos añadidos. Total: {puntos_usuario.puntos}")

        # Otorgar insignia por primer curso completado
        if ProgresoCurso.objects.filter(usuario=instance.usuario, completado=True).count() == 1:
            otorgar_insignia(instance.usuario, INSIGNIA_PRIMER_CURSO_COMPLETADO)
        
        # Ejemplo de insignia basada en puntos totales (después de añadir los puntos del curso)
        # Esta señal se dispara al guardar PuntosUsuario, por lo que es redundante aquí.
        # La eliminaremos de aquí para evitar chequeos duplicados, ya que `otorgar_insignias_a_usuario`
        # en PuntosUsuario.post_save ya manejará esto.
        # if puntos_usuario.puntos >= 100:
        #     otorgar_insignia(instance.usuario, INSIGNIA_DEDICACION)
            
@receiver(post_save, sender=PuntosUsuario)
def asignar_nivel_y_otorgar_insignias_por_puntos(sender, instance, created, **kwargs):
    """
    Asigna el nivel correspondiente y otorga insignias basadas en puntos
    cada vez que los puntos de un usuario son actualizados.
    """
    # Evitar bucle infinito cuando la señal llama a save()
    if kwargs.get('raw', False): # 'raw' es True si se está cargando desde una fixture
        return
    if hasattr(instance, '_processing_signal') and instance._processing_signal:
        return

    instance._processing_signal = True # Set flag

    try:
        puntos_actuales = instance.puntos
        usuario = instance.usuario
        nivel_cambiado = False
        insignias_otorgadas_por_puntos = False # Flag para insignias basadas en puntos

        # --- Lógica de Asignación de Nivel ---
        nivel_alcanzado = Nivel.objects.filter(puntos_minimos__lte=puntos_actuales).order_by('puntos_minimos').last()

        if nivel_alcanzado and instance.nivel_actual != nivel_alcanzado:
            instance.nivel_actual = nivel_alcanzado
            nivel_cambiado = True
            logger.debug(f"{usuario.username} ha alcanzado el nivel: {nivel_alcanzado.nombre}")
        elif not nivel_alcanzado and instance.nivel_actual is not None:
            instance.nivel_actual = None
            nivel_cambiado = True
            logger.debug(f"{usuario.username} ya no tiene un nivel asignado.")

        # --- Lógica de Otorgar Insignias Basadas en Puntos ---
        # Obtener todas las insignias disponibles que requieren puntos
        insignias_por_puntos = Insignia.objects.filter(puntos_requeridos__gt=0) # Asume que insignias con puntos_requeridos = 0 no se otorgan por puntos
        
        for insignia in insignias_por_puntos:
            if puntos_actuales >= insignia.puntos_requeridos:
                # otoga_insignia ya maneja get_or_create y los mensajes de depuración
                if otorgar_insignia(usuario, insignia.nombre): # Si se otorgó una nueva insignia
                    insignias_otorgadas_por_puntos = True

        # Solo guarda si hubo un cambio en el nivel o se otorgó una nueva insignia basada en puntos
        if nivel_cambiado:
            instance.save(update_fields=['nivel_actual']) # Guardar solo el campo nivel_actual para evitar bucles si no hay más cambios
    finally:
        instance._processing_signal = False # Clear flag

# Nota: Eliminar la señal `otorgar_insignias_a_usuario` separada si no se usa más,
# ya que la lógica se ha integrado en `asignar_nivel_y_otorgar_insignias_por_puntos`.
# Si necesitas ambas separadas por alguna razón, asegúrate de que no haya bucles.