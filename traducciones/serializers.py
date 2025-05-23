# traducciones/serializers.py
from rest_framework import serializers
from .models import CategoriaSenda, Senda

class CategoriaSendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaSenda
        fields = '__all__'

class SendaSerializer(serializers.ModelSerializer):
    # Este campo 'categoria_id' será para ESCRIBIR el ID de la categoría
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaSenda.objects.all(),
        source='categoria', # Mapea este campo de entrada al campo 'categoria' del modelo
        write_only=True,    # Este campo solo se usará para escritura (POST/PUT)
        required=False,     # Hazlo opcional si una senda puede no tener categoría al inicio
        allow_null=True     # Permite que la categoría sea nula al escribir
    )
    # Este campo 'categoria' será para LEER la información completa de la categoría
    categoria = CategoriaSendaSerializer(read_only=True)

    class Meta:
        model = Senda
        fields = '__all__'
        # Excluye 'categoria_id' de la salida si no quieres que se muestre como un campo separado en la lectura
        # Pero inclúyelo en la escritura. '__all__' lo incluye por defecto.
        # Puedes usar 'extra_kwargs' si quieres ocultarlo de la lectura
        extra_kwargs = {
            'categoria_id': {'write_only': True} # Asegura que solo es para escritura
        }