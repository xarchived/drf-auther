from typing import Any

from django.conf import settings
from fancy.serializers import FancySerializer
from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework.relations import PrimaryKeyRelatedField

from auther.models import Domain, Role, User, Perm
# region basic serializers
from auther.utils import generate_password, hash_password


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
        exclude = ['password']


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
    name = CharField(min_length=3, max_length=9, allow_blank=True)
    regex = CharField(min_length=1, max_length=64)
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
    username = CharField(min_length=6, max_length=64)
    password = CharField(min_length=8, max_length=64, write_only=True, required=False)
    avatar_pic = CharField(min_length=64, max_length=128, required=False)
    domain_id = PrimaryKeyRelatedField(source='domain', queryset=Domain.objects.all(), required=False)
    domain = BasicDomainSerializer(required=False)
    role_id = PrimaryKeyRelatedField(source='role', queryset=Role.objects.all(), required=False)
    role = BasicRoleSerializer(required=False)

    class Meta:
        model = User
        exclude = []

    def create(self, validated_data: dict) -> Any:
        random_password = None

        # Create a role with same name as model and add it to user
        default_role = settings.AUTHER.get('DEFAULT_ROLE')
        if default_role and 'role_id' not in self.initial_data and 'role' not in self.initial_data:
            role_name = self.Meta.model.__name__.lower()
            role, _ = Role.objects.get_or_create(name=role_name)
            self.validated_data['role_id'] = role.id

        # If password is not provided we generate a random one
        if 'password' not in self.initial_data:
            random_password = generate_password(8)
            hashed_password = str(hash_password(random_password), encoding='ascii')
            self.validated_data['password'] = hashed_password

        # Store record into database
        user = super(UserSerializer, self).create(validated_data)

        # Disable write only option for random passwords
        if random_password:
            self.fields['password'].write_only = False
            user.password = str(random_password, encoding='ascii')

        return user


# endregion

# noinspection PyAbstractClass
class LoginSerializer(serializers.Serializer):
    username = CharField(min_length=4, max_length=64)
    password = CharField(min_length=6, max_length=64, write_only=True)
