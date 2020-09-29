import json
from base64 import b64encode
from os import urandom

import bcrypt
from django.conf import settings
from redisary import Redisary
from rest_framework.exceptions import APIException

from auther.models import User

tokens = Redisary(db=settings.AUTHER['REDIS_DB'])


def authenticate(request):
    username = request.data['username']
    password = request.data['password']

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise APIException('Username not found')

    if bcrypt.checkpw(password.encode('utf-8'), bytes(user.password, encoding='utf-8')):
        return user

    raise APIException('Wrong password')


def login(user):
    roles = user.roles.all()
    token = b64encode(urandom(33))
    token = str(token, encoding='utf-8')

    payload = {
        'id': user.id,
        'name': user.name,
        'username': user.username,
        'avatar_pic': user.avatar_pic,
        'domain_id': user.domain_id,
        'roles': [role.name for role in roles]
    }
    tokens[token] = json.dumps(payload)

    return token
