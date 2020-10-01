import json
import re

import bcrypt
from django.conf import settings
from redisary import Redisary
from rest_framework.exceptions import APIException, NotFound

from auther.models import Perm


# TODO: Raise better exceptions
class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.tokens = Redisary(db=settings.AUTHER['REDIS_DB'])

        self.roles = dict()
        for perm in Perm.objects.all():
            self.roles[perm.method + perm.re_path] = {role.name for role in perm.roles.all()}

    @staticmethod
    def _hash_password(request):
        password_pattern = b'"password"\\s*:\\s*".*"'
        password = re.search(password_pattern, request.body)
        if request.path != settings.AUTHER['LOGIN_PAGE'] and password:
            password = password.group(0)
            password = password[13:-1]
            hashed = bcrypt.hashpw(password, bcrypt.gensalt())
            new_password = b'"password": "' + hashed + b'"'
            request._body = re.sub(password_pattern, new_password, request.body)

    def _check_permission(self, request):
        if not self.roles:
            return

        k = request.method + request.path
        r = self.roles.get(k)

        if r is None:
            raise NotFound()

        if not r:
            return

        if request.auth is None:
            raise APIException('Token dose not exist')

        if set(request.auth.roles) & r:
            return

        raise APIException('Access Denied')

    def _fill_user(self, request):
        request.auth = None
        token = request.COOKIES.get(settings.AUTHER['TOKEN_NAME'])
        if token and token in self.tokens:
            request.auth = json.loads(self.tokens[token])

    def __call__(self, request):
        self._fill_user(request)
        self._check_permission(request)
        self._hash_password(request)

        return self.get_response(request)
