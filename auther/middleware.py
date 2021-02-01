import json
import re
from typing import Any, Callable

from django.conf import settings
from django.http import JsonResponse
from redisary import Redisary
from rest_framework.exceptions import PermissionDenied, NotAuthenticated, APIException
from rest_framework.request import Request

from auther.models import Role, Domain, User
from auther.utils import hash_password


class AuthMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response
        self.tokens = Redisary(db=settings.AUTHER['REDIS_DB'])
        self.password_pattern = b'"password"\\s*:\\s*".*?"'

        self.patterns = dict()
        for role in Role.objects.all():
            self.patterns[role.name] = [perm.regex for perm in role.perms.all()]

        empty = True
        for role, pattern in self.patterns.items():
            if pattern:
                empty = False

        if empty:
            self.patterns = dict()

    def _authorized(self, request: Request, role: str) -> bool:
        request_line = f'{request.method} {request.path}'

        for pattern in self.patterns[role]:
            if re.match(pattern, request_line):
                return True

        return False

    def _fill_credential(self, request: Request) -> None:
        request.credential = None
        token = request.COOKIES.get(settings.AUTHER['TOKEN_NAME'])
        if token and token in self.tokens:
            raw = json.loads(self.tokens[token])
            user = User(
                id=raw['id'],
                name=raw['name'],
                username=raw['username'],
                avatar_token=raw['avatar_token'],
                role=Role(name=raw['role']),
                domain=Domain(address=raw['domain']))
            request.credential = user

    def _check_permission(self, request: Request) -> None:
        if not self.patterns:
            return

        if self._authorized(request, 'anyone'):
            return

        if request.credential is None:
            raise NotAuthenticated('Token dose not exist')

        if self._authorized(request, request.credential.role.name):
            return

        raise PermissionDenied('Access Denied')

    def _extract_password(self, request: Request) -> bytes:
        password = re.search(self.password_pattern, request.body)
        if password:
            password = password.group(0)
            password = password[13:-1]
            return password
        return b''

    def _hash_password(self, request: Request) -> None:
        password = self._extract_password(request)
        if request.path != settings.AUTHER['LOGIN_PAGE'] and password:
            hashed = hash_password(password)
            password_field = b'"password": "' + hashed + b'"'
            request._body = re.sub(self.password_pattern, password_field, request.body)

    def __call__(self, request: Request) -> Any:
        try:
            self._fill_credential(request)
            self._check_permission(request)
            self._hash_password(request)
        except Exception as e:
            if isinstance(e, APIException):
                return JsonResponse(
                    data={'detail': e.detail},
                    status=e.status_code)
            return JsonResponse({'detail': 'Authentication error'}, status=500)

        return self.get_response(request)
