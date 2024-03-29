from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class LimitExceededError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('child limit exceeded')


class PrivilegeError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('privilege is not suffice')


class AlreadySet(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('already exists')
