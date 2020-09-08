from rest_framework.relations import PrimaryKeyRelatedField

from api.models import User, Role, Perm
from fancy.serializers import FancySerializer


# region basic serializers

class BasicPermSerializer(FancySerializer):
    class Meta:
        model = Perm
        exclude = []


class BasicRoleSerializer(FancySerializer):
    class Meta:
        model = Role
        exclude = ['perms']


class BasicUserSerializer(FancySerializer):
    class Meta:
        model = User
        exclude = ['password', 'roles']


# endregion


# region serializers

class PermSerializer(FancySerializer):
    class Meta:
        model = Perm
        exclude = []


class RoleSerializer(FancySerializer):
    users_ids = PrimaryKeyRelatedField(source='users', many=True, queryset=User.objects.all(), required=False)
    users = BasicUserSerializer(many=True, required=False)
    perms_ids = PrimaryKeyRelatedField(source='perms', many=True, queryset=Perm.objects.all(), required=False)
    perms = BasicPermSerializer(many=True, required=False)

    class Meta:
        model = Role
        exclude = []


class UserSerializer(FancySerializer):
    roles_ids = PrimaryKeyRelatedField(source='roles', many=True, queryset=Role.objects.all(), required=False)
    roles = BasicRoleSerializer(many=True, required=False)

    class Meta:
        model = User
        exclude = ['password']

# endregion
