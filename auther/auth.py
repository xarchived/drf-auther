import importlib
import pickle

from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.request import Request

from auther.db import passwords, tokens
from auther.models import User, Session
from auther.settings import OTP_PROVIDER, MAX_SESSIONS, TOKEN_NAME
from auther.utils import generate_token, check_password


def authenticate(username: str, phone: int, password: str, otp: bool = False) -> User:
    identifier: str
    user: User

    # fetch user if exists or raise an error
    try:
        if username:
            user = User.objects.get(username=username)
            identifier = username
        elif phone:
            user = User.objects.get(phone=phone)
            identifier = str(phone)
        else:
            raise ValidationError('Identifier is not provided')
    except User.DoesNotExist:
        raise AuthenticationFailed('Username and/or password is wrong')

    # check if user is available
    if user.deleted_at:
        raise AuthenticationFailed('User has been removed')
    if not user.active:
        raise AuthenticationFailed('Account is not active')
    if user.expire and user.expire < timezone.now():
        raise AuthenticationFailed('Account has expire')

    # check session limitation
    session = Session.objects.filter(user_id=user.id)
    if len(session) > MAX_SESSIONS:
        raise AuthenticationFailed('Maximum number of sessions exceeded')

    if otp:
        if not passwords.exists(identifier):
            raise AuthenticationFailed('Username and/or password is wrong')

        if password == passwords.get(identifier):
            passwords.delete(identifier)
            return user

    elif check_password(password, user.password):
        return user

    raise AuthenticationFailed('Username and/or password is wrong')


def login(user: User, user_agent: str) -> str:
    token = generate_token()

    session = Session(token=token, user=user, user_agent=user_agent)
    session.save()

    tokens.set(token, pickle.dumps(user))

    return token


# noinspection PyProtectedMember
def logout(request: Request) -> None:
    token_name = TOKEN_NAME

    if token_name in request._request.COOKIES:
        passwords.delete(request._request.COOKIES[token_name])


# noinspection PyUnresolvedReferences
def send_otp(receptor: int, token: str) -> dict:
    otp_provider = importlib.import_module(OTP_PROVIDER)
    passwords.set(receptor, token, ex=OTP_EXPIRE)
    return otp_provider.send_otp(
        receptor=receptor,
        token=token,
    )
