from typing import Any

from django.db.models import Model
from rest_framework.fields import CharField, DateTimeField, BooleanField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework.validators import UniqueValidator

from auther.models import Domain, Role, User, Session, Perm
from auther.simples import SimpleDomainSerializer, SimpleRoleSerializer, SimpleUserSerializer, SimplePermSerializer
from auther.utils import generate_password, hash_password
from fancy.serializers import CommonFieldsSerializer


class PermSerializer(CommonFieldsSerializer):
    name = CharField(
        min_length=3,
        max_length=9,
        allow_blank=True,
        validators=[UniqueValidator(queryset=Perm.objects.all())],
    )
    regex = CharField(min_length=1, max_length=64)
    roles_ids = PrimaryKeyRelatedField(
        source='roles',
        many=True,
        queryset=Role.objects.all(),
        required=False,
        allow_null=True,
    )
    roles = SimpleRoleSerializer(many=True, read_only=True)

    class Meta:
        model = Perm
        fields = [
            *CommonFieldsSerializer.Meta.fields,
            'name',
            'regex',
            'roles_ids',
            'roles',
        ]


class RoleSerializer(CommonFieldsSerializer):
    name = CharField(
        min_length=3,
        max_length=64,
        validators=[UniqueValidator(queryset=Role.objects.all())],
    )
    perms_ids = PrimaryKeyRelatedField(
        source='perms',
        many=True,
        queryset=Perm.objects.all(),
        required=False,
        allow_null=True,
    )
    perms = SimplePermSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = [
            *CommonFieldsSerializer.Meta.fields,
            'name',
            'perms_ids',
            'perms',
        ]


class DomainSerializer(CommonFieldsSerializer):
    name = CharField(
        min_length=1,
        max_length=99,
        validators=[UniqueValidator(queryset=Domain.objects.all())],
    )
    address = CharField(min_length=4, max_length=99)

    class Meta:
        model = Domain
        fields = [
            *CommonFieldsSerializer.Meta.fields,
            'name',
            'address',
        ]


class UserSerializer(CommonFieldsSerializer):
    name = CharField(min_length=3, max_length=64, required=False, allow_null=True, allow_blank=True)
    username = CharField(
        min_length=6,
        max_length=64,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = CharField(min_length=8, max_length=64, write_only=True, required=False, allow_null=True)
    active = BooleanField(allow_null=True, default=True, required=False)
    expire = DateTimeField(allow_null=True, required=False)
    domain_id = PrimaryKeyRelatedField(
        source='domain',
        queryset=Domain.objects.all(),
        required=False,
        allow_null=True,
    )
    domain = SimpleDomainSerializer(read_only=True)
    roles_ids = PrimaryKeyRelatedField(
        source='roles',
        many=True,
        queryset=Role.objects.all(),
        required=False,
        allow_null=True,
    )
    roles = SimpleRoleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            *CommonFieldsSerializer.Meta.fields,
            'name',
            'username',
            'password',
            'active',
            'expire',
            'domain_id',
            'domain',
            'roles_ids',
            'roles',
        ]

    @staticmethod
    def _hash_password_field(validated_data: dict) -> dict:
        if 'password' in validated_data:
            validated_data['password'] = hash_password(password=validated_data['password'])

        return validated_data

    def create(self, validated_data: dict) -> Any:
        random_password = None

        # If there is a password field we will hash it
        validated_data = self._hash_password_field(validated_data)

        # If password is not provided we generate a random one
        if 'password' not in self.initial_data:
            random_password = generate_password(8)
            validated_data['password'] = random_password
            validated_data = self._hash_password_field(validated_data)

        # Store record into database
        user = super().create(validated_data)

        # Disable write only option for random passwords
        if random_password:
            self.fields['password'].write_only = False
            user.password = random_password

        return user

    def update(self, instance: Model, validated_data: dict) -> Any:
        # If there is a password field we will hash it
        validated_data = self._hash_password_field(validated_data)

        return super().update(instance=instance, validated_data=validated_data)


class SessionSerializer(ModelSerializer):
    token = CharField(required=True, min_length=64, max_length=64)
    user_id = PrimaryKeyRelatedField(
        source='user',
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )
    user = SimpleUserSerializer(read_only=True)
    user_agent = CharField(required=True, min_length=200)
    inserted_at = DateTimeField(read_only=True)

    class Meta:
        model = Session
        fields = [
            'id',
            'token',
            'user_id',
            'user',
            'user_agent',
            'inserted_at',
        ]


# noinspection PyAbstractClass
class LoginSerializer(Serializer):
    username = CharField(min_length=4, max_length=64)
    password = CharField(min_length=5, max_length=64, write_only=True)
