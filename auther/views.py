from rest_framework import viewsets

from auther.models import Domain, Role, Perm, User
from auther.serializers import DomainSerializer, PermSerializer, RoleSerializer, UserSerializer


class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer


class PermViewSet(viewsets.ModelViewSet):
    queryset = Perm.objects.all()
    serializer_class = PermSerializer


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
