import json

from django.utils import timezone
from redisary import Redisary
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from auther.models import User, Session
from auther.settings import REDIS_DB, MAX_SESSIONS, TOKEN_NAME
from auther.utils import generate_token, check_password

tokens = Redisary(db=REDIS_DB)


def authenticate(username: str, password: str) -> User:
    # fetch user if exists or raise an error
    try:
        user = User.objects.get(username=username)
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

    # check user password
    if check_password(password, user.password):
        return user

    raise AuthenticationFailed('Username and/or password is wrong')


def login(user: User, user_agent: str) -> str:
    token = generate_token()

    session = Session(token=token, user=user, user_agent=user_agent)
    session.save()

    tokens[token] = json.dumps(user.as_simple_dict)

    return token


# noinspection PyProtectedMember
def logout(request: Request) -> None:
    token_name = TOKEN_NAME

    if token_name in request._request.COOKIES:
        del tokens[request._request.COOKIES[token_name]]
