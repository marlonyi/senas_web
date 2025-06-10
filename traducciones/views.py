# traducciones/views.py
from rest_framework import viewsets, permissions
from .models import CategoriaSenda, Senda
from .serializers import CategoriaSendaSerializer, SendaSerializer
from django_filters.rest_framework import DjangoFilterBackend # ¡Añade esta importación!
from rest_framework import filters # ¡Añade esta importación!

class CategoriaSendaViewSet(viewsets.ModelViewSet):
    queryset = CategoriaSenda.objects.all()
    serializer_class = CategoriaSendaSerializer
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['activo'] # Puedes filtrar por si está activa o no
    search_fields = ['nombre', 'descripcion'] 

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Solo los administradores pueden crear/actualizar/eliminar categorías
            self.permission_classes = [permissions.IsAdminUser]
        else:
            # Todos los usuarios autenticados pueden ver las categorías
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

class SendaViewSet(viewsets.ModelViewSet):
    queryset = Senda.objects.all()
    serializer_class = SendaSerializer
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['activo', 'categoria'] # Filtrar por si está activa o por ID de categoría
    search_fields = ['titulo', 'contenido']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Solo los administradores pueden crear/actualizar/eliminar sendas
            self.permission_classes = [permissions.IsAdminUser]
        else:
            # Todos los usuarios autenticados pueden ver las sendas
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    # Si quieres que la categoría se pueda asignar por ID al crear/actualizar,
    # necesitarías adaptar el serializer o sobrescribir el create/update aquí.
    # Por ejemplo, para que el campo 'categoria' acepte un ID al escribir:
    # class SendaSerializer(serializers.ModelSerializer):
    #    categoria = serializers.PrimaryKeyRelatedField(queryset=CategoriaSenda.objects.all(), write_only=True)
    #    categoria_data = CategoriaSendaSerializer(read_only=True, source='categoria') # Para mostrar la categoría al leer
    #    class Meta:
    #        model = Senda
    #        fields = '__all__'
    #        extra_kwargs = {'categoria': {'write_only': True}}