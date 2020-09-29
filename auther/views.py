from django.conf import settings
from fancy.viewsets import FancyViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from auther.auth import authenticate, login
from auther.models import Domain, Role, Perm, User
from auther.serializers import DomainSerializer, PermSerializer, RoleSerializer, UserSerializer, LoginSerializer


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


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(request)
        token = login(user)

        response = Response()
        response.set_cookie(
            settings.AUTHER['TOKEN_NAME'],
            token,
            httponly=settings.AUTHER['TOKEN_HTTPONLY'],
            max_age=settings.AUTHER['TOKEN_EXPIRE'])

        return response
