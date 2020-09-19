from fancy.viewsets import FancyViewSet

from auther.models import Domain, Role, Perm, User
from auther.serializers import DomainSerializer, PermSerializer, RoleSerializer, UserSerializer


class DomainViewSet(FancyViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer


class PermViewSet(FancyViewSet):
    queryset = Perm.objects.all()
    serializer_class = PermSerializer


class RoleViewSet(FancyViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class UserViewSet(FancyViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
