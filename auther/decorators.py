from rest_framework.request import Request

from auther.exceptions import PrivilegeError
from auther.models import Role
from fancy.views import CredentialAPIView


def check_privilege(func):
    def get_user_level(self: CredentialAPIView) -> int:
        role = self.credential.roles.first()

        if not role:
            raise PrivilegeError('You do not have any privilege')

        return role.level

    def get_request_level(self, request: Request) -> int:
        highest_level = 0

        try:
            user = self.get_object()
            for role in user.roles.all():
                if role.level > highest_level:
                    highest_level = role.level
        except AssertionError:
            pass

        if 'roles_ids' in request.data:
            for role_id in request.data['roles_ids']:
                role = Role.objects.get(id=role_id)
                if role.level > highest_level:
                    highest_level = role.level

        return highest_level

    def wrapper(*args, **kwargs):
        self = args[0]
        request = args[1]
        user_level = get_user_level(self)
        request_level = get_request_level(self, request)

        if request_level >= user_level:
            raise PrivilegeError()

        return func(*args, **kwargs)

    return wrapper
