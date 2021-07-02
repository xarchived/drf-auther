from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from auther.auth import authenticate, login, logout
from auther.models import Perm, Role, Domain, User
from auther.serializers import (
    PermSerializer,
    RoleSerializer,
    DomainSerializer,
    UserSerializer,
    LoginSerializer,
)
from auther.settings import (
    TOKEN_NAME,
    TOKEN_DOMAIN,
    TOKEN_PATH,
    TOKEN_HTTPONLY,
    TOKEN_EXPIRE,
    TOKEN_SAMESITE,
    TOKEN_SECURE,
)
from fancy.viewsets import FancyViewSet


class PermViewSet(FancyViewSet):
    queryset = Perm.objects.all()
    serializer_class = PermSerializer


class RoleViewSet(FancyViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class DomainViewSet(FancyViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer


class UserViewSet(FancyViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(request.data['username'], request.data['password'])
        token = login(user, request.headers['User-Agent'])

        # TODO: write a function to do this
        response = Response({
            'id': user.id,
            'name': user.name,
            'roles': [role.name for role in user.roles.all()],
        })

        response.set_cookie(
            TOKEN_NAME,
            token,
            domain=TOKEN_DOMAIN,
            path=TOKEN_PATH,
            httponly=TOKEN_HTTPONLY,
            max_age=TOKEN_EXPIRE,
            samesite=TOKEN_SAMESITE,
            secure=TOKEN_SECURE,
        )

        return response


class LogoutView(APIView):
    # noinspection PyMethodMayBeStatic
    def post(self, request: Request) -> Response:
        logout(request)

        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(
            TOKEN_NAME,
            domain=TOKEN_DOMAIN,
            path=TOKEN_PATH,
        )
        return response
