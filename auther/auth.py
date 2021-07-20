import json
from rest_framework.request import Request
from rest_framework.response import Response
from django.utils import timezone
from redisary import Redisary
from rest_framework.exceptions import AuthenticationFailed
from typing import Callable
from auther.models import User, Session
from auther.utils import generate_token, check_password
from auther.settings import (
    TOKEN_NAME,
    TOKEN_DOMAIN,
    TOKEN_PATH,
    TOKEN_HTTPONLY,
    TOKEN_EXPIRE,
    TOKEN_SAMESITE,
    TOKEN_SECURE,
    MAX_SESSIONS,
    REDIS_DB,

)

tokens = Redisary(db=REDIS_DB)
otp_token = Redisary(host='127.0.0.1', db=2, expire=120)


def login_authenticate(request: Request, get_serializer: Callable, otp: bool) -> Response:
    serializer = get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = authenticate(request.data['username'], request.data['password'], otp)
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


def authenticate(username: str, password: str, otp: bool) -> User:
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise AuthenticationFailed('Username and/or password is wrong')

    if user.deleted_at:
        raise AuthenticationFailed('User has been removed')

    if not user.active:
        raise AuthenticationFailed('Account is not active')

    if user.expire and user.expire < timezone.now():
        raise AuthenticationFailed('Account has expire')

    session = Session.objects.filter(user_id=user.id)
    if len(session) > MAX_SESSIONS:
        raise AuthenticationFailed('Maximum number of sessions exceeded')

    if otp:
        if username in otp_token:
            user_token = otp_token[username]
            if password == user_token:
                del otp_token[username]  # delete username from redis
                return user
    else:
        check_password(password, user.password)
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
