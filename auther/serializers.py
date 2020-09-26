from fancy.serializers import FancySerializer
from rest_framework.fields import CharField
from rest_framework.relations import PrimaryKeyRelatedField

from auther.models import Domain, Role, User, Perm


# region basic serializers

class BasicDomainSerializer(FancySerializer):
    class Meta:
        model = Domain
        exclude = []


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

class DomainSerializer(FancySerializer):
    name = CharField(min_length=1, max_length=99)
    address = CharField(min_length=4, max_length=99)
    users_ids = PrimaryKeyRelatedField(source='users', many=True, queryset=User.objects.all(), required=False)
    users = BasicUserSerializer(many=True, required=False)

    class Meta:
        model = Domain
        exclude = []


class PermSerializer(FancySerializer):
    method = CharField(min_length=3, max_length=9)
    re_path = CharField(min_length=1, max_length=64)
    roles_ids = PrimaryKeyRelatedField(source='roles', many=True, queryset=Role.objects.all(), required=False)
    roles = BasicRoleSerializer(many=True, required=False)

    class Meta:
        model = Perm
        exclude = []


class RoleSerializer(FancySerializer):
    name = CharField(min_length=3, max_length=64)
    users_ids = PrimaryKeyRelatedField(source='users', many=True, queryset=User.objects.all(), required=False)
    users = BasicUserSerializer(many=True, required=False)
    perms_ids = PrimaryKeyRelatedField(source='perms', many=True, queryset=Perm.objects.all(), required=False)
    perms = BasicPermSerializer(many=True, required=False)

    class Meta:
        model = Role
        exclude = []


class UserSerializer(FancySerializer):
    name = CharField(min_length=3, max_length=64)
    username = CharField(min_length=4, max_length=64)
    password = CharField(min_length=6, max_length=64, write_only=True)
    avatar_pic = CharField(min_length=64, max_length=128)
    domain_id = PrimaryKeyRelatedField(source='domain', queryset=Domain.objects.all(), required=False)
    domain = BasicDomainSerializer(required=False)
    roles_ids = PrimaryKeyRelatedField(source='roles', many=True, queryset=Role.objects.all(), required=False)
    roles = BasicRoleSerializer(many=True, required=False)

    class Meta:
        model = User
        exclude = []

# endregion
