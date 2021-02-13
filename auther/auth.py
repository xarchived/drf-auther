import json

from django.conf import settings
from django.utils import timezone
from redisary import Redisary
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from auther.models import User, Session
from auther.utils import generate_token, check_password

tokens = Redisary(db=settings.AUTHER['REDIS_DB'])


def authenticate(request: Request) -> User:
    username = request.data['username']
    password = request.data['password']

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
    if len(session) > settings.AUTHER['MAX_SESSIONS']:
        raise AuthenticationFailed('Maximum number of sessions exceeded')

    if check_password(password, user.password):
        return user

    raise AuthenticationFailed('Username and/or password is wrong')


def login(request: Request, user: User) -> str:
    token = generate_token()

    session = Session(token=token, user=user, user_agent=request.headers['User-Agent'])
    session.save()

    payload = {
        'id': user.id,
        'name': user.name,
        'username': user.username,
        'avatar_token': user.avatar_token,
        'domain': user.domain.address if user.domain else None,
        'role': user.role.name if user.role else None
    }
    tokens[token] = json.dumps(payload)

    return token


# noinspection PyProtectedMember
def logout(request: Request) -> None:
    token_name = settings.AUTHER['TOKEN_NAME']

    if token_name in request._request.COOKIES:
        del tokens[request._request.COOKIES[token_name]]
