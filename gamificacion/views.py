from django.shortcuts import render

# Create your views here.
# gamificacion/views.py
from rest_framework import viewsets
from .models import Logro, LogroUsuario
from .serializers import LogroSerializer, LogroUsuarioSerializer

class LogroViewSet(viewsets.ModelViewSet):
    queryset = Logro.objects.all()
    serializer_class = LogroSerializer

class LogroUsuarioViewSet(viewsets.ModelViewSet):
    queryset = LogroUsuario.objects.all()
    serializer_class = LogroUsuarioSerializer