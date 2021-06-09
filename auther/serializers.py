from typing import Any

from django.db.models import Model
from rest_framework import serializers, fields, relations

from auther import models, simples, settings
from auther.utils import generate_password, hash_password


class PermSerializer(serializers.ModelSerializer):
    name = fields.CharField(min_length=3, max_length=9, allow_blank=True)
    regex = fields.CharField(min_length=1, max_length=64)
    roles_ids = relations.PrimaryKeyRelatedField(
        source='roles',
        many=True,
        queryset=models.Role.objects.all(),
        required=False,
        allow_null=True,
    )
    roles = simples.SimpleRoleSerializer(many=True, read_only=True)

    class Meta:
        model = models.Perm
        exclude = []


class RoleSerializer(serializers.ModelSerializer):
    name = fields.CharField(min_length=3, max_length=64)
    users_ids = relations.PrimaryKeyRelatedField(
        source='users',
        many=True,
        queryset=models.User.objects.all(),
        required=False,
        allow_null=True,
    )
    users = simples.SimpleUserSerializer(many=True, read_only=True)
    perms_ids = relations.PrimaryKeyRelatedField(
        source='perms',
        many=True,
        queryset=models.Perm.objects.all(),
        required=False,
        allow_null=True,
    )
    perms = simples.SimplePermSerializer(many=True, read_only=True)

    class Meta:
        model = models.Role
        exclude = []


class DomainSerializer(serializers.ModelSerializer):
    name = fields.CharField(min_length=1, max_length=99)
    address = fields.CharField(min_length=4, max_length=99)
    users_ids = relations.PrimaryKeyRelatedField(
        source='users',
        many=True,
        queryset=models.User.objects.all(),
        required=False,
        allow_null=True,
    )
    users = simples.SimpleUserSerializer(many=True, read_only=True)

    class Meta:
        model = models.Domain
        exclude = []


class UserSerializer(serializers.ModelSerializer):
    name = fields.CharField(min_length=3, max_length=64, required=False, allow_null=True, allow_blank=True)
    username = fields.CharField(min_length=6, max_length=64)
    password = fields.CharField(min_length=8, max_length=64, write_only=True, required=False, allow_null=True)
    avatar_token = fields.CharField(min_length=64, max_length=128, required=False, allow_null=True)
    active = fields.BooleanField(allow_null=True, default=True, required=False)
    expire = fields.DateTimeField(allow_null=True, required=False)
    domain_id = relations.PrimaryKeyRelatedField(
        source='domain',
        queryset=models.Domain.objects.all(),
        required=False,
        allow_null=True,
    )
    domain = simples.SimpleDomainSerializer(read_only=True)
    role_id = relations.PrimaryKeyRelatedField(
        source='role',
        queryset=models.Role.objects.all(),
        required=False,
        allow_null=True,
    )
    role = simples.SimpleRoleSerializer(read_only=True)

    class Meta:
        model = models.User
        exclude = []

    @staticmethod
    def _hash_password_field(validated_data: dict) -> None:
        if 'password' in validated_data:
            validated_data['password'] = hash_password(password=validated_data['password'])

    def create(self, validated_data: dict) -> Any:
        random_password = None

        # If there is a password field we will hash it
        self._hash_password_field(validated_data)

        # Create a role with same name as model and add it to user
        default_role = settings.DEFAULT_ROLE
        if default_role and 'role_id' not in self.initial_data and 'role' not in self.initial_data:
            role_name = self.Meta.model.__name__.lower()
            role, _ = models.Role.objects.get_or_create(name=role_name)
            self.validated_data['role_id'] = role.id

        # If password is not provided we generate a random one
        if 'password' not in self.initial_data:
            random_password = generate_password(8)
            self.validated_data['password'] = random_password
            self._hash_password_field(validated_data)

        # Store record into database
        user = super(UserSerializer, self).create(validated_data)

        # Disable write only option for random passwords
        if random_password:
            self.fields['password'].write_only = False
            user.password = random_password

        return user

    def update(self, instance: Model, validated_data: dict) -> Any:
        # If there is a password field we will hash it
        self._hash_password_field(validated_data)

        return super(UserSerializer, self).update(instance=instance, validated_data=validated_data)


class SessionSerializer(serializers.ModelSerializer):
    token = fields.CharField(required=True, min_length=64, max_length=64)
    user_id = relations.PrimaryKeyRelatedField(
        source='user',
        queryset=models.User.objects.all(),
        required=False,
        allow_null=True,
    )
    user = simples.SimpleUserSerializer(read_only=True)
    user_agent = fields.CharField(required=True, min_length=200)
    inserted_at = fields.DateTimeField(read_only=True)

    class Meta:
        model = models.Session
        exclude = []


# noinspection PyAbstractClass
class LoginSerializer(serializers.Serializer):
    username = fields.CharField(min_length=4, max_length=64)
    password = fields.CharField(min_length=6, max_length=64, write_only=True)
