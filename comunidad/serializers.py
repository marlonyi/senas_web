# comunidad/serializers.py
from rest_framework import serializers
from .models import Foro, Comentario, MeGustaComentario
from django.contrib.auth import get_user_model

User = get_user_model()

# Un serializer simple para el usuario, para anidarlo sin exponer todo el modelo de User
class UserSerializerForCommunity(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class MeGustaComentarioSerializer(serializers.ModelSerializer):
    usuario = UserSerializerForCommunity(read_only=True) # Muestra el usuario que dio el like

    class Meta:
        model = MeGustaComentario
        fields = ['id', 'comentario', 'usuario', 'fecha_creacion'] # Se explícitan los campos
        read_only_fields = ['usuario', 'fecha_creacion'] # Usuario y fecha se gestionan automáticamente

class ComentarioSerializer(serializers.ModelSerializer):
    autor = UserSerializerForCommunity(read_only=True)
    me_gustas_count = serializers.SerializerMethodField()
    respuestas = serializers.SerializerMethodField()

    parent_comentario_id = serializers.PrimaryKeyRelatedField(
        queryset=Comentario.objects.all(), source='parent_comentario', write_only=True, required=False, allow_null=True
    )

    # --- MODIFICACIÓN CLAVE AQUÍ ---
    # Definimos el campo 'foro' explícitamente para controlar su comportamiento en la entrada/salida.
    # - `PrimaryKeyRelatedField`: Espera un ID de la clave primaria (del Foro).
    # - `queryset=Foro.objects.all()`: Es necesario para que DRF valide que el ID del foro exista.
    # - `write_only=True`: Significa que este campo solo se usa para la entrada (POST/PUT/PATCH)
    #                      y no se incluirá en la salida JSON del comentario (GET).
    #                      Esto es útil porque el foro ya está implícito en la URL o no queremos
    #                      repetirlo en la salida detallada de un comentario.
    # - `required=False`: Esto es lo CRUCIAL para resolver el error. Le dice al serializador
    #                     que no es obligatorio que este campo sea enviado en el cuerpo de la solicitud
    #                     cuando se crea un comentario. Esto permite que la vista/acción (en `ForoViewSet`)
    #                     lo inyecte programáticamente después de la validación inicial.
    foro = serializers.PrimaryKeyRelatedField(queryset=Foro.objects.all(), write_only=True, required=False)
    # --- FIN DE LA MODIFICACIÓN CLAVE ---

    class Meta:
        model = Comentario
        # Mantenemos 'foro' en los campos generales para que el serializador sepa que existe,
        # pero su comportamiento de entrada/salida ya está definido por la línea explícita de 'foro' arriba.
        fields = [
            'id', 'foro', 'autor', 'contenido', 'fecha_creacion',
            'fecha_actualizacion', 'parent_comentario', 'parent_comentario_id',
            'respuestas', 'me_gustas_count'
        ]
        # Asegúrate de que 'foro' NO esté en esta lista si lo has definido explícitamente arriba
        # con write_only=True o si se va a asignar en la vista.
        read_only_fields = ['autor', 'fecha_creacion', 'fecha_actualizacion']

    def get_me_gustas_count(self, obj):
        return obj.me_gustas.count() # Cuenta los likes relacionados

    def get_respuestas(self, obj):
        # Filtra las respuestas que no tienen un parent_comentario
        # Si quieres anidamiento de N niveles, tendrías que usar RecursiveField o similar
        # Para este caso, vamos a traer solo las respuestas directas
        # Se asegura que la recursión solo ocurra para comentarios de nivel superior
        if obj.parent_comentario is None:
            # Aquí, ComentarioSerializer se llama a sí mismo para serializar las respuestas
            # y se pasa el contexto para control de profundidad en escenarios más complejos.
            return ComentarioSerializer(obj.respuestas.all(), many=True, context=self.context).data
        return [] # Si ya es una respuesta, no mostramos sus respuestas para evitar recursión infinita en la salida.


class ForoSerializer(serializers.ModelSerializer):
    creador = UserSerializerForCommunity(read_only=True) # Muestra el creador del foro
    comentarios_count = serializers.SerializerMethodField() # Para mostrar cuántos comentarios tiene

    # Para anidar los comentarios principales del foro (nivel 0 de profundidad)
    # Solo los comentarios que NO tienen un parent_comentario.
    comentarios_principales = serializers.SerializerMethodField() # Cambiado el nombre del campo

    class Meta:
        model = Foro
        # Se listan explícitamente los campos para mayor claridad y control
        fields = [
            'id', 'titulo', 'descripcion', 'fecha_creacion',
            'creador', 'activo', 'comentarios_count', 'comentarios_principales'
        ]
        read_only_fields = ['creador', 'fecha_creacion']

    def get_comentarios_count(self, obj):
        # Cuenta todos los comentarios relacionados con el foro
        return obj.comentarios.count()

    def get_comentarios_principales(self, obj):
        # Obtiene solo los comentarios de nivel superior para este foro
        # Es decir, aquellos que no son respuestas a otros comentarios.
        main_comments_qs = obj.comentarios.filter(parent_comentario__isnull=True)
        # Pasar el contexto es importante para que los ComentarioSerializer anidados también lo reciban.
        return ComentarioSerializer(main_comments_qs, many=True, context=self.context).data