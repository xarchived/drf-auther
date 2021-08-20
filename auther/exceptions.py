from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException


class PrivilegeError(APIException):
    status_code = 403
    default_detail = _('privilege is not suffice')


class AlreadySet(APIException):
    status_code = 409
    default_detail = _('Already exists')
