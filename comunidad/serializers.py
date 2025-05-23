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
        fields = '__all__'
        read_only_fields = ['usuario', 'fecha_creacion'] # Usuario y fecha se gestionan automáticamente

class ComentarioSerializer(serializers.ModelSerializer):
    autor = UserSerializerForCommunity(read_only=True) # Muestra el autor del comentario
    me_gustas_count = serializers.SerializerMethodField() # Para mostrar cuántos likes tiene

    # Para comentarios anidados (respuestas)
    respuestas = serializers.SerializerMethodField()

    class Meta:
        model = Comentario
        fields = '__all__'
        read_only_fields = ['autor', 'fecha_creacion', 'fecha_actualizacion'] # Autor y fechas se gestionan automáticamente

    def get_me_gustas_count(self, obj):
        return obj.me_gustas.count() # Cuenta los likes relacionados

    def get_respuestas(self, obj):
        # Filtra las respuestas que no tienen un parent_comentario
        # Si quieres anidamiento de N niveles, tendrías que usar RecursiveField o similar
        # Para este caso, vamos a traer solo las respuestas directas
        respuestas_qs = obj.respuestas.filter(parent_comentario=obj)
        return ComentarioSerializer(respuestas_qs, many=True, read_only=True).data # Recursivo

    # Para poder asignar el parent_comentario al crear/actualizar
    def to_internal_value(self, data):
        # Si parent_comentario_id viene en la entrada, úsalo para asignar el parent_comentario
        if 'parent_comentario_id' in data:
            data['parent_comentario'] = data.pop('parent_comentario_id')
        return super().to_internal_value(data)

class ForoSerializer(serializers.ModelSerializer):
    creador = UserSerializerForCommunity(read_only=True) # Muestra el creador del foro
    comentarios_count = serializers.SerializerMethodField() # Para mostrar cuántos comentarios tiene

    # Opcional: para anidar los comentarios principales del foro
    # comentarios = ComentarioSerializer(many=True, read_only=True, source='comentarios')

    class Meta:
        model = Foro
        fields = '__all__'
        read_only_fields = ['creador', 'fecha_creacion']

    def get_comentarios_count(self, obj):
        return obj.comentarios.count() # Cuenta los comentarios relacionados