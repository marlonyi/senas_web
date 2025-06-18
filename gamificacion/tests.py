# cursos/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone

from .models import Curso, Modulo, Leccion, Actividad, \
    ProgresoCurso, ProgresoModulo, ProgresoLeccion, ProgresoActividad
from . import signals as cursos_signals

# Importar modelos de gamificacion para crear instancias relacionadas
from gamificacion.models import PuntosUsuario, Nivel, Insignia, InsigniaUsuario
from gamificacion.signals import (
    PUNTOS_POR_ACTIVIDAD, PUNTOS_POR_LECCION, PUNTOS_POR_MODULO, PUNTOS_POR_CURSO,
    INSIGNIA_PRIMERA_ACTIVIDAD_COMPLETADA, INSIGNIA_PRIMERA_LECCION_COMPLETADA,
    INSIGNIA_PRIMER_MODULO_COMPLETADO, INSIGNIA_PRIMER_CURSO_COMPLETADO,
    asignar_nivel_y_otorgar_insignias_por_puntos,
    manejar_progreso_actividad_gamificacion,
    manejar_progreso_leccion_gamificacion,
    manejar_progreso_modulo_gamificacion,
    manejar_progreso_curso_gamificacion
)

class CursosSignalsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Desconectar todas las señales de gamificación de forma global para la clase de test.
        # Esto asegura que no interfieran con los tests unitarios de cascada.
        post_save.disconnect(asignar_nivel_y_otorgar_insignias_por_puntos, sender=PuntosUsuario)
        post_save.disconnect(manejar_progreso_actividad_gamificacion, sender=ProgresoActividad)
        post_save.disconnect(manejar_progreso_leccion_gamificacion, sender=ProgresoLeccion)
        post_save.disconnect(manejar_progreso_modulo_gamificacion, sender=ProgresoModulo)
        post_save.disconnect(manejar_progreso_curso_gamificacion, sender=ProgresoCurso)

        # Desconectar las señales de cursos que el test de integración va a reconectar.
        # Las dejamos desconectadas para los tests unitarios de progresión.
        post_save.disconnect(cursos_signals.actualizar_progreso_modulo, sender=ProgresoLeccion)
        post_save.disconnect(cursos_signals.actualizar_progreso_leccion_desde_actividad, sender=ProgresoActividad)
        post_save.disconnect(cursos_signals.actualizar_progreso_curso, sender=ProgresoModulo)


    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Reconectar las señales de gamificación y cursos que fueron desconectadas globalmente.
        # Esto es vital para no afectar otros tests o el funcionamiento normal de la aplicación.
        post_save.connect(asignar_nivel_y_otorgar_insignias_por_puntos, sender=PuntosUsuario)
        post_save.connect(manejar_progreso_actividad_gamificacion, sender=ProgresoActividad)
        post_save.connect(manejar_progreso_leccion_gamificacion, sender=ProgresoLeccion)
        post_save.connect(manejar_progreso_modulo_gamificacion, sender=ProgresoModulo)
        post_save.connect(manejar_progreso_curso_gamificacion, sender=ProgresoCurso)

        post_save.connect(cursos_signals.actualizar_progreso_modulo, sender=ProgresoLeccion)
        post_save.connect(cursos_signals.actualizar_progreso_leccion_desde_actividad, sender=ProgresoActividad)
        post_save.connect(cursos_signals.actualizar_progreso_curso, sender=ProgresoModulo)


    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Crear datos de gamificación mínimos
        self.nivel_novato = Nivel.objects.create(nombre="Novato", puntos_minimos=0)
        self.nivel_aprendiz = Nivel.objects.create(nombre="Aprendiz", puntos_minimos=50)
        self.nivel_experto = Nivel.objects.create(nombre="Experto", puntos_minimos=100)
        self.puntos_usuario = PuntosUsuario.objects.create(usuario=self.user, puntos=0, nivel_actual=self.nivel_novato)

        # Crear insignias (TODAS las que podrían ser referenciadas por constantes)
        self.insignia_primeros_pasos = Insignia.objects.create(
            nombre=INSIGNIA_PRIMERA_ACTIVIDAD_COMPLETADA, puntos_requeridos=PUNTOS_POR_ACTIVIDAD, descripcion="Completó su primera actividad."
        )
        self.insignia_aprendiz_leccion = Insignia.objects.create(
            nombre=INSIGNIA_PRIMERA_LECCION_COMPLETADA, puntos_requeridos=PUNTOS_POR_LECCION, descripcion="Completó su primera lección."
        )
        self.insignia_explorador_modulo = Insignia.objects.create(
            nombre=INSIGNIA_PRIMER_MODULO_COMPLETADO, puntos_requeridos=PUNTOS_POR_MODULO, descripcion="Completó un módulo."
        )
        self.insignia_maestro_curso = Insignia.objects.create(
            nombre=INSIGNIA_PRIMER_CURSO_COMPLETADO, puntos_requeridos=PUNTOS_POR_CURSO, descripcion="Completó un curso."
        )
        self.insignia_dedicacion = Insignia.objects.create(
            nombre="Dedicación", puntos_requeridos=100, descripcion="Alcanzó 100 puntos."
        )

        # Reconectar las señales de `cursos` SOLO para este test (ya que las desconectamos en setUpClass)
        # Esto aplica a todos los tests de la clase excepto el de integración si lo manejamos aparte.
        # Aquí las reconectamos porque los tests unitarios sí dependen de la cascada de cursos.
        post_save.connect(cursos_signals.actualizar_progreso_modulo, sender=ProgresoLeccion)
        post_save.connect(cursos_signals.actualizar_progreso_leccion_desde_actividad, sender=ProgresoActividad)
        post_save.connect(cursos_signals.actualizar_progreso_curso, sender=ProgresoModulo)


    def tearDown(self):
        # En los tearDowns individuales, no se necesita hacer nada si las conexiones
        # se gestionan en setUpClass/tearDownClass.
        pass

    # --- Tests para la cascada de ProgresoActividad -> ProgresoLeccion ---
    def test_actividad_completa_leccion(self):
        curso = Curso.objects.create(nombre="Curso Test", descripcion="...", nivel="Básico")
        modulo = Modulo.objects.create(curso=curso, nombre="Modulo Test", descripcion="...", orden=1)
        leccion = Leccion.objects.create(modulo=modulo, titulo="Leccion Test", contenido_texto="...", orden=1)
        actividad1 = Actividad.objects.create(leccion=leccion, pregunta="Pregunta 1", tipo_actividad='pregunta_respuesta', puntos=10)
        actividad2 = Actividad.objects.create(leccion=leccion, pregunta="Pregunta 2", tipo_actividad='pregunta_respuesta', puntos=10)

        # Crear progreso para la lección (no completado inicialmente)
        progreso_leccion, created = ProgresoLeccion.objects.get_or_create(usuario=self.user, leccion=leccion)
        self.assertFalse(progreso_leccion.completado)
        self.assertFalse(progreso_leccion.puntos_otorgados)

        # Completar la primera actividad
        progreso_actividad1 = ProgresoActividad.objects.create(
            usuario=self.user, actividad=actividad1, completado=True, fecha_completado=timezone.now()
        )

        # Verificar que la lección NO esté completada todavía (solo una actividad de dos)
        progreso_leccion.refresh_from_db()
        self.assertFalse(progreso_leccion.completado)
        self.assertFalse(progreso_leccion.puntos_otorgados)

        # Completar la segunda actividad
        progreso_actividad2 = ProgresoActividad.objects.create(
            usuario=self.user, actividad=actividad2, completado=True, fecha_completado=timezone.now()
        )

        # Verificar que la lección AHORA esté completada
        progreso_leccion.refresh_from_db()
        self.assertTrue(progreso_leccion.completado)
        self.assertIsNotNone(progreso_leccion.fecha_completado)
        self.assertFalse(progreso_leccion.puntos_otorgados)


    # --- Test para ProgresoLeccion -> ProgresoModulo ---
    def test_leccion_completa_modulo(self):
        curso = Curso.objects.create(nombre="Curso Test", descripcion="...", nivel="Básico")
        modulo = Modulo.objects.create(curso=curso, nombre="Modulo Test", descripcion="...", orden=1)
        leccion1 = Leccion.objects.create(modulo=modulo, titulo="Leccion 1", contenido_texto="...", orden=1)
        leccion2 = Leccion.objects.create(modulo=modulo, titulo="Leccion 2", contenido_texto="...", orden=2) # <-- CORRECCIÓN AQUI: leccion2

        # Crear progreso para el módulo (no completado inicialmente)
        progreso_modulo, created = ProgresoModulo.objects.get_or_create(usuario=self.user, modulo=modulo)
        self.assertFalse(progreso_modulo.completado)
        self.assertFalse(progreso_modulo.puntos_otorgados)

        # Completar la primera lección
        progreso_leccion1 = ProgresoLeccion.objects.create(
            usuario=self.user, leccion=leccion1, completado=True, fecha_completado=timezone.now()
        )

        # Verificar que el módulo NO esté completado todavía
        progreso_modulo.refresh_from_db()
        self.assertFalse(progreso_modulo.completado)
        self.assertFalse(progreso_modulo.puntos_otorgados)

        # Completar la segunda lección
        progreso_leccion2 = ProgresoLeccion.objects.create(
            usuario=self.user, leccion=leccion2, completado=True, fecha_completado=timezone.now() # <-- CORRECCIÓN AQUI: leccion2
        )

        # Verificar que el módulo AHORA esté completado
        progreso_modulo.refresh_from_db()
        self.assertTrue(progreso_modulo.completado)
        self.assertIsNotNone(progreso_modulo.fecha_completado)
        self.assertFalse(progreso_modulo.puntos_otorgados)


    # --- Test para ProgresoModulo -> ProgresoCurso ---
    def test_modulo_completa_curso(self):
        curso = Curso.objects.create(nombre="Curso Test", descripcion="...", nivel="Básico")
        modulo1 = Modulo.objects.create(curso=curso, nombre="Modulo 1", descripcion="...", orden=1)
        modulo2 = Modulo.objects.create(curso=curso, nombre="Modulo 2", descripcion="...", orden=2)

        # Crear progreso para el curso (no completado inicialmente)
        progreso_curso, created = ProgresoCurso.objects.get_or_create(usuario=self.user, curso=curso)
        self.assertFalse(progreso_curso.completado)
        self.assertFalse(progreso_curso.puntos_otorgados)

        # Completar el primer módulo
        progreso_modulo1 = ProgresoModulo.objects.create(
            usuario=self.user, modulo=modulo1, completado=True, fecha_completado=timezone.now()
        )

        # Verificar que el curso NO esté completado todavía
        progreso_curso.refresh_from_db()
        self.assertFalse(progreso_curso.completado)
        self.assertFalse(progreso_curso.puntos_otorgados)

        # Completar el segundo módulo
        progreso_modulo2 = ProgresoModulo.objects.create(
            usuario=self.user, modulo=modulo2, completado=True, fecha_completado=timezone.now()
        )

        # Verificar que el curso AHORA esté completado
        progreso_curso.refresh_from_db()
        self.assertTrue(progreso_curso.completado)
        self.assertIsNotNone(progreso_curso.fecha_completado)
        self.assertFalse(progreso_curso.puntos_otorgados)


    # --- Test de Integración: Actividad -> Lección -> Módulo -> Curso (y puntos/insignias) ---
    def test_full_progression_with_gamification(self):
        # En este test, RECONECTAMOS TODAS las señales, para probar la integración completa
        # Se usa `connect` sin `dispatch_uid` para reconectar solo para este test.
        # Las conexiones globales ya están manejadas en setUpClass/tearDownClass.
        post_save.connect(asignar_nivel_y_otorgar_insignias_por_puntos, sender=PuntosUsuario)
        post_save.connect(manejar_progreso_actividad_gamificacion, sender=ProgresoActividad)
        post_save.connect(manejar_progreso_leccion_gamificacion, sender=ProgresoLeccion)
        post_save.connect(manejar_progreso_modulo_gamificacion, sender=ProgresoModulo)
        post_save.connect(manejar_progreso_curso_gamificacion, sender=ProgresoCurso)

        post_save.connect(cursos_signals.actualizar_progreso_modulo, sender=ProgresoLeccion)
        post_save.connect(cursos_signals.actualizar_progreso_leccion_desde_actividad, sender=ProgresoActividad)
        post_save.connect(cursos_signals.actualizar_progreso_curso, sender=ProgresoModulo)


        # Crear una estructura completa de curso con una actividad por lección, una lección por módulo, un módulo por curso
        curso = Curso.objects.create(nombre="Curso Integración", descripcion="...", nivel="Avanzado")
        modulo = Modulo.objects.create(curso=curso, nombre="Modulo Integración", descripcion="...", orden=1)
        leccion = Leccion.objects.create(modulo=modulo, titulo="Leccion Integración", contenido_texto="...", orden=1)
        actividad = Actividad.objects.create(leccion=leccion, pregunta="Pregunta Integración", tipo_actividad='pregunta_respuesta', puntos=10)

        # Antes de completar, nada debe estar completo y puntos deben ser 0
        self.puntos_usuario.refresh_from_db()
        self.assertEqual(self.puntos_usuario.puntos, 0)
        self.assertEqual(self.user.insignias_obtenidas.count(), 0)

        # Crear y completar la actividad final, lo que debería disparar toda la cascada
        progreso_actividad = ProgresoActividad.objects.create(
            usuario=self.user,
            actividad=actividad,
            completado=True,
            fecha_completado=timezone.now()
        )

        # Refresh todas las instancias para obtener el estado actual de la DB
        progreso_curso = ProgresoCurso.objects.get(usuario=self.user, curso=curso)
        progreso_modulo = ProgresoModulo.objects.get(usuario=self.user, modulo=modulo)
        progreso_leccion = ProgresoLeccion.objects.get(usuario=self.user, leccion=leccion)
        progreso_actividad.refresh_from_db()
        self.puntos_usuario.refresh_from_db()

        # Verificar que todo el progreso esté completado
        self.assertTrue(progreso_actividad.completado)
        self.assertTrue(progreso_leccion.completado)
        self.assertTrue(progreso_modulo.completado)
        self.assertTrue(progreso_curso.completado)

        # Verificar que se otorgaron los puntos correctamente (suma de todos los puntos de nivel)
        expected_points = PUNTOS_POR_ACTIVIDAD + PUNTOS_POR_LECCION + PUNTOS_POR_MODULO + PUNTOS_POR_CURSO
        self.assertEqual(self.puntos_usuario.puntos, expected_points)
        self.assertTrue(progreso_actividad.puntos_otorgados)
        self.assertTrue(progreso_leccion.puntos_otorgados)
        self.assertTrue(progreso_modulo.puntos_otorgados)
        self.assertTrue(progreso_curso.puntos_otorgados)

        # Verificar que se otorgaron las insignias relevantes
        self.assertTrue(self.user.insignias_obtenidas.filter(insignia__nombre=INSIGNIA_PRIMERA_ACTIVIDAD_COMPLETADA).exists())
        self.assertTrue(self.user.insignias_obtenidas.filter(insignia__nombre=INSIGNIA_PRIMERA_LECCION_COMPLETADA).exists())
        self.assertTrue(self.user.insignias_obtenidas.filter(insignia__nombre=INSIGNIA_PRIMER_MODULO_COMPLETADO).exists())
        self.assertTrue(self.user.insignias_obtenidas.filter(insignia__nombre=INSIGNIA_PRIMER_CURSO_COMPLETADO).exists())
        self.assertGreaterEqual(self.user.insignias_obtenidas.count(), 4)

        # Desconectar señales al final de este test específico de integración
        post_save.disconnect(asignar_nivel_y_otorgar_insignias_por_puntos, sender=PuntosUsuario)
        post_save.disconnect(manejar_progreso_actividad_gamificacion, sender=ProgresoActividad)
        post_save.disconnect(manejar_progreso_leccion_gamificacion, sender=ProgresoLeccion)
        post_save.disconnect(manejar_progreso_modulo_gamificacion, sender=ProgresoModulo)
        post_save.disconnect(manejar_progreso_curso_gamificacion, sender=ProgresoCurso)

        post_save.disconnect(cursos_signals.actualizar_progreso_modulo, sender=ProgresoLeccion)
        post_save.disconnect(cursos_signals.actualizar_progreso_leccion_desde_actividad, sender=ProgresoActividad)
        post_save.disconnect(cursos_signals.actualizar_progreso_curso, sender=ProgresoModulo)