# gamificacion/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PuntosUsuario, Insignia, InsigniaUsuario
from cursos.models import ProgresoActividad, ProgresoLeccion, ProgresoModulo, ProgresoCurso # Importa tus modelos de Progreso

# Define los puntos que se otorgarán
PUNTOS_POR_ACTIVIDAD = 5
PUNTOS_POR_LECCION = 10
PUNTOS_POR_MODULO = 20
PUNTOS_POR_CURSO = 50

# Define los IDs de las insignias y los puntos requeridos (puedes crear estas insignias en el admin más tarde)
# Es una buena práctica usar IDs o nombres únicos. Aquí usamos nombres.
INSIGNIA_PRIMERA_ACTIVIDAD_COMPLETADA = "Primer Pasos (Actividad)"
INSIGNIA_PRIMERA_LECCION_COMPLETADA = "Aprendiz (Lección)"
INSIGNIA_PRIMER_MODULO_COMPLETADO = "Explorador (Módulo)"
INSIGNIA_PRIMER_CURSO_COMPLETADO = "Maestro (Curso)"
INSIGNIA_DEDICACION = "Dedicatoria (100 Puntos)" # Ejemplo de insignia basada en puntos

def obtener_o_crear_puntos_usuario(user):
    """Helper para obtener o inicializar los puntos de un usuario."""
    puntos_usuario, created = PuntosUsuario.objects.get_or_create(usuario=user)
    if created:
        print(f"DEBUG: Se crearon PuntosUsuario para {user.username} con 0 puntos.")
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
            print(f"DEBUG: Insignia '{nombre_insignia}' otorgada a {usuario.username}.")
            return True
        else:
            print(f"DEBUG: {usuario.username} ya tiene la insignia '{nombre_insignia}'.")
            return False
    except Insignia.DoesNotExist:
        print(f"ERROR: La insignia '{nombre_insignia}' no existe. Creala en el admin.")
        return False

@receiver(post_save, sender=ProgresoActividad)
def manejar_progreso_actividad_gamificacion(sender, instance, created, **kwargs):
    if instance.completado and (created or instance.pk): # Asegúrate que la actividad está completa y no es la primera vez que se guarda en completado
        print(f"DEBUG: Señal gamificación: ProgresoActividad completado para {instance.usuario.username}.")
        puntos_usuario = obtener_o_crear_puntos_usuario(instance.usuario)
        puntos_usuario.puntos += PUNTOS_POR_ACTIVIDAD
        puntos_usuario.save()
        print(f"DEBUG: {PUNTOS_POR_ACTIVIDAD} puntos añadidos. Total: {puntos_usuario.puntos}")

        # Otorgar insignia por primera actividad completada
        if PuntosUsuario.objects.filter(usuario=instance.usuario, puntos__gte=PUNTOS_POR_ACTIVIDAD).count() == 1: # Solo si es la primera actividad
            otorgar_insignia(instance.usuario, INSIGNIA_PRIMERA_ACTIVIDAD_COMPLETADA)


@receiver(post_save, sender=ProgresoLeccion)
def manejar_progreso_leccion_gamificacion(sender, instance, created, **kwargs):
    if instance.completado and (created or instance.pk):
        print(f"DEBUG: Señal gamificación: ProgresoLeccion completado para {instance.usuario.username}.")
        puntos_usuario = obtener_o_crear_puntos_usuario(instance.usuario)
        puntos_usuario.puntos += PUNTOS_POR_LECCION
        puntos_usuario.save()
        print(f"DEBUG: {PUNTOS_POR_LECCION} puntos añadidos. Total: {puntos_usuario.puntos}")

        # Otorgar insignia por primera lección completada
        if ProgresoLeccion.objects.filter(usuario=instance.usuario, completado=True).count() == 1:
            otorgar_insignia(instance.usuario, INSIGNIA_PRIMERA_LECCION_COMPLETADA)


@receiver(post_save, sender=ProgresoModulo)
def manejar_progreso_modulo_gamificacion(sender, instance, created, **kwargs):
    if instance.completado and (created or instance.pk):
        print(f"DEBUG: Señal gamificación: ProgresoModulo completado para {instance.usuario.username}.")
        puntos_usuario = obtener_o_crear_puntos_usuario(instance.usuario)
        puntos_usuario.puntos += PUNTOS_POR_MODULO
        puntos_usuario.save()
        print(f"DEBUG: {PUNTOS_POR_MODULO} puntos añadidos. Total: {puntos_usuario.puntos}")

        # Otorgar insignia por primer módulo completado
        if ProgresoModulo.objects.filter(usuario=instance.usuario, completado=True).count() == 1:
            otorgar_insignia(instance.usuario, INSIGNIA_PRIMER_MODULO_COMPLETADO)

@receiver(post_save, sender=ProgresoCurso)
def manejar_progreso_curso_gamificacion(sender, instance, created, **kwargs):
    if instance.completado and (created or instance.pk):
        print(f"DEBUG: Señal gamificación: ProgresoCurso completado para {instance.usuario.username}.")
        puntos_usuario = obtener_o_crear_puntos_usuario(instance.usuario)
        puntos_usuario.puntos += PUNTOS_POR_CURSO
        puntos_usuario.save()
        print(f"DEBUG: {PUNTOS_POR_CURSO} puntos añadidos. Total: {puntos_usuario.puntos}")

        # Otorgar insignia por primer curso completado
        if ProgresoCurso.objects.filter(usuario=instance.usuario, completado=True).count() == 1:
            otorgar_insignia(instance.usuario, INSIGNIA_PRIMER_CURSO_COMPLETADO)

        # Ejemplo de insignia basada en puntos totales (después de añadir los puntos del curso)
        if puntos_usuario.puntos >= 100:
            otorgar_insignia(instance.usuario, INSIGNIA_DEDICACION)