from rest_framework.serializers import ModelSerializer

from auther.models import Role, Perm, Domain, User


class SimpleRoleSerializer(ModelSerializer):
    class Meta:
        model = Role
        exclude = ['perms']


class SimplePermSerializer(ModelSerializer):
    class Meta:
        model = Perm
        exclude = []


class SimpleDomainSerializer(ModelSerializer):
    class Meta:
        model = Domain
        exclude = []


class SimpleUserSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']
