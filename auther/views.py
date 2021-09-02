from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from auther.auth import authenticate, login, logout, send_otp
from auther.decorators import check_privilege
from auther.exceptions import AlreadySet
from auther.models import Perm, Role, Domain, User, Session
from auther.serializers import (
    PermSerializer,
    RoleSerializer,
    DomainSerializer,
    UserSerializer,
    LoginSerializer,
    SendOtpSerializer,
    SetRoleSerializer,
    SessionSerializer,
)
from auther.settings import (
    TOKEN_NAME,
    TOKEN_DOMAIN,
    TOKEN_PATH,
    TOKEN_HTTPONLY,
    TOKEN_EXPIRE,
    TOKEN_SAMESITE,
    TOKEN_SECURE,
    DEFAULT_ROLE,
)
from auther.utils import generate_otp
from fancy.decorators import credential_required
from fancy.views import CredentialAPIView


class MeViewSet(GenericViewSet, CredentialAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_user(self) -> User:
        return get_object_or_404(self.get_queryset(), self.credential.id)

    def retrieve(self, request: Request) -> Response:
        if not self.credential:
            return Response()

        user = self.get_user()
        serializer = self.get_serializer(user)

        return Response(serializer.data)

    @credential_required
    def update(self, request: Request, *args, **kwargs) -> Response:
        partial = kwargs.pop('partial', False)

        user = self.get_user()
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @credential_required
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def set_role(self, request):
        if not self.credential:
            raise NotAuthenticated('No credential found')

        serializer = SetRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(User, pk=self.credential.id)
        if user.roles.count() != 0:
            raise AlreadySet('already has a role')

        user.roles.add(serializer.validated_data['role'])
        user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data)


class PermViewSet(ModelViewSet):
    queryset = Perm.objects.all()
    serializer_class = PermSerializer


class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class DomainViewSet(ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer


class UserViewSet(ModelViewSet, CredentialAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @credential_required
    @check_privilege
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

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


class SessionViewSet(ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


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

            if DEFAULT_ROLE:
                role = Role.objects.get(name=DEFAULT_ROLE)
                user.roles.add(role)

        otp = generate_otp(5)
        send_otp(phone, otp)

        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data.get('username'),
            phone=serializer.validated_data.get('phone'),
            password=serializer.validated_data.get('password'),
            otp=request.query_params.get('method') == 'otp',
        )
        token = login(user, request.headers['User-Agent'])

        serializer = UserSerializer(user)
        response = Response(serializer.data)

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
