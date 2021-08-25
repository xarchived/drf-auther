import pickle
import re
from typing import Any, Callable

from django.http import JsonResponse
from rest_framework.exceptions import PermissionDenied, NotAuthenticated, APIException
from rest_framework.request import Request

from auther.db import tokens
from auther.models import Role
from auther.settings import TOKEN_NAME, LOGIN_PAGE, DEBUG


class AuthMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

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

    @staticmethod
    def _fill_credential(request: Request) -> None:
        request.credential = None
        token = request.COOKIES.get(TOKEN_NAME)

        if not token:
            return

        if not tokens.exists(token):
            if request.path == LOGIN_PAGE:
                return

            raise NotAuthenticated('Token not found')

        request.credential = pickle.loads(tokens.get(token))

    def _check_permission(self, request: Request) -> None:
        if not self.patterns:
            return

        if self._authorized(request, 'anyone'):
            return

        if request.credential is None:
            raise NotAuthenticated('Token dose not exist')

        for role in request.credential.roles:
            if self._authorized(request, role.name):
                return

        raise PermissionDenied('Access Denied')

    def __call__(self, request: Request) -> Any:
        try:
            self._fill_credential(request)
            self._check_permission(request)
        except Exception as e:
            if DEBUG:
                raise e

            if isinstance(e, APIException):
                return JsonResponse(
                    data={'detail': e.detail},
                    status=e.status_code,
                )
            return JsonResponse({'detail': 'Authentication error'}, status=500)

        return self.get_response(request)
