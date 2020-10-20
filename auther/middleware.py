import json
import re

from django.conf import settings
from redisary import Redisary
from rest_framework.exceptions import PermissionDenied, NotAuthenticated

from auther.models import Perm, Role
from auther.utils import hash_password


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.tokens = Redisary(db=settings.AUTHER['REDIS_DB'])

        self.patterns = dict()
        for role in Role.objects.all():
            self.patterns[role.name] = [perm.regex for perm in role.perms.all()]

        empty = True
        for role, pattern in self.patterns.items():
            if pattern:
                empty = False

        if empty:
            self.patterns = dict()

        if self.patterns:
            self.patterns['anyone'] = []
            for perm in Perm.objects.all():
                if not perm.roles.all():
                    self.patterns['anyone'].append(perm.regex)
                    for role in self.patterns:
                        self.patterns[role].append(perm.regex)

    def _authorized(self, request, role):
        request_line = f'{request.method} {request.path}'

        for pattern in self.patterns[role]:
            if re.match(pattern, request_line):
                return True

        return False

    def _fill_user(self, request):
        request.auth = None
        token = request.COOKIES.get(settings.AUTHER['TOKEN_NAME'])
        if token and token in self.tokens:
            request.auth = json.loads(self.tokens[token])

    def _check_permission(self, request):
        if not self.patterns:
            return

        if self._authorized(request, 'anyone'):
            return

        if request.auth is None:
            raise NotAuthenticated('Token dose not exist')

        if self._authorized(request, request.auth['role']):
            return

        raise PermissionDenied('Access Denied')

    @staticmethod
    def _hash_password(request):
        password_pattern = b'"password"\\s*:\\s*".*"'
        password = re.search(password_pattern, request.body)
        if request.path != settings.AUTHER['LOGIN_PAGE'] and password:
            password = password.group(0)
            password = password[13:-1]
            hashed = hash_password(password)
            password_field = b'"password": "' + hashed + b'"'
            request._body = re.sub(password_pattern, password_field, request.body)

    def __call__(self, request):
        self._fill_user(request)
        self._check_permission(request)
        self._hash_password(request)

        return self.get_response(request)
