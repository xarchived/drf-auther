from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from auther.auth import authenticate, login, logout
from auther.decorators import check_privilege
from auther.models import Perm, Role, Domain, User
from auther.serializers import (
    PermSerializer,
    RoleSerializer,
    DomainSerializer,
    UserSerializer,
    LoginSerializer,
    SendOtpSerializer,
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
from auther.utils import generate_otp, send_otp
from fancy.decorators import credential_required
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


class SendOtpView(GenericAPIView):
    serializer_class = SendOtpSerializer

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        user = User.objects.filter(phone=phone).first()
        if not user:
            user = User(phone=phone)
            user.save()

        otp = generate_otp(5)
        send_otp(phone, otp)

        return Response(status=status.HTTP_200_OK)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(request.data['username'], request.data['password'])
        token = login(user, request.headers['User-Agent'])

        response = Response(user.as_simple_dict)

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
