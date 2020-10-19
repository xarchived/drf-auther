import json

import bcrypt
from django.conf import settings
from redisary import Redisary
from rest_framework.exceptions import APIException

from auther.models import User
from auther.utils import generate_token

tokens = Redisary(db=settings.AUTHER['REDIS_DB'])


def authenticate(request):
    username = request.data['username']
    password = request.data['password']

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise APIException('Username not found')

    if bcrypt.checkpw(bytes(password, encoding='utf-8'), bytes(user.password, encoding='utf-8')):
        return user

    raise APIException('Wrong password')


def login(user):
    token = generate_token()

    payload = {
        'id': user.id,
        'name': user.name,
        'username': user.username,
        'avatar_pic': user.avatar_pic,
        'domain_id': user.domain_id,
        'role': user.role.name
    }
    tokens[token] = json.dumps(payload)

    return token
