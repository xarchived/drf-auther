import json
import re
from typing import Any, Callable

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from redisary import Redisary
from rest_framework.exceptions import PermissionDenied, NotAuthenticated

from auther.models import Perm, Role, Domain, User
from auther.utils import hash_password


class AuthMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response
        self.tokens = Redisary(db=settings.AUTHER['REDIS_DB'])
        self.password_pattern = b'"password"\\s*:\\s*".*"'

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

    def _authorized(self, request: WSGIRequest, role: str) -> bool:
        request_line = f'{request.method} {request.path}'

        for pattern in self.patterns[role]:
            if re.match(pattern, request_line):
                return True

        return False

    def _fill_user(self, request: WSGIRequest) -> None:
        request.credential = None
        token = request.COOKIES.get(settings.AUTHER['TOKEN_NAME'])
        if token and token in self.tokens:
            raw = json.loads(self.tokens[token])
            user = User(
                id=raw['id'],
                name=raw['name'],
                username=raw['username'],
                avatar_pic=raw['avatar_pic'],
                role=Role(name=raw['role']),
                domain=Domain(address=raw['domain']))
            request.credential = user

    def _check_permission(self, request: WSGIRequest) -> None:
        if not self.patterns:
            return

        if self._authorized(request, 'anyone'):
            return

        if hasattr(request, 'credential'):
            if request.credential is None:
                raise NotAuthenticated('Token dose not exist')

            if self._authorized(request, request.credential.role.name):
                return

        raise PermissionDenied('Access Denied')

    def _extract_password(self, request: WSGIRequest) -> bytes:
        password = re.search(self.password_pattern, request.body)
        if password:
            password = password.group(0)
            password = password[13:-1]
            return password
        return b''

    def _hash_password(self, request: WSGIRequest) -> None:
        password = self._extract_password(request)
        if request.path != settings.AUTHER['LOGIN_PAGE'] and password:
            hashed = hash_password(password)
            password_field = b'"password": "' + hashed + b'"'
            request._body = re.sub(self.password_pattern, password_field, request.body)

    def __call__(self, request: WSGIRequest) -> Any:
        self._fill_user(request)
        self._check_permission(request)
        self._hash_password(request)

        return self.get_response(request)
