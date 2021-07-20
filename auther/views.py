from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from auther.auth import logout
from auther.decorators import check_privilege
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
from fancy.decorators import credential_required
from fancy.viewsets import FancyViewSet
from auther.auth import login_authenticate


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

    @credential_required
    @check_privilege
    def create(self, request, *args, **kwargs):
        return super().create(request=request, *args, **kwargs)

    @credential_required
    @check_privilege
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @credential_required
    @check_privilege
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @credential_required
    @check_privilege
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request: Request) -> Response:
        return login_authenticate(request, self.get_serializer, otp=False)


class OtpLoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request: Request) -> Response:
        return login_authenticate(request, self.get_serializer, otp=True)


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
