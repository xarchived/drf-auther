from rest_framework import viewsets

from api.models import User, Role, Perm
from api.serializers import PermSerializer, RoleSerializer, UserSerializer


class PermViewSet(viewsets.ModelViewSet):
    queryset = Perm.objects.all()
    serializer_class = PermSerializer


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
