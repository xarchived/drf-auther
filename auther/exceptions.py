from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class PrivilegeError(APIException):
    status_code = 403
    default_detail = _('privilege is not suffice')
