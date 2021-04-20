from django.conf import settings
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from auther.auth import authenticate, login, logout
from auther.models import Domain, Role, Perm, User
from auther.serializers import DomainSerializer, PermSerializer, RoleSerializer, UserSerializer, LoginSerializer
from fancy.viewsets import FancyViewSet


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

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(request)
        token = login(request, user)

        response = Response({
            'id': user.id,
            'name': user.name,
            'avatar_token': user.avatar_token,
            'role': user.role.name if user.role else None,
        })

        response.set_cookie(
            settings.AUTHER['TOKEN_NAME'],
            token,
            domain=settings.AUTHER['TOKEN_DOMAIN'],
            path=settings.AUTHER['TOKEN_PATH'],
            httponly=settings.AUTHER['TOKEN_HTTPONLY'],
            max_age=settings.AUTHER['TOKEN_EXPIRE'],
            samesite=settings.AUTHER['TOKEN_SAMESITE'],
            secure=settings.AUTHER['TOKEN_SECURE'],
        )

        return response


class LogoutView(APIView):
    # noinspection PyMethodMayBeStatic
    def post(self, request: Request) -> Response:
        logout(request)

        return Response(status=status.HTTP_204_NO_CONTENT)
