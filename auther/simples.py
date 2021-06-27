from rest_framework.serializers import ModelSerializer

from auther.models import Role, Perm, Domain, User
from fancy.serializers import CommonFieldsSerializer


class SimplePermSerializer(CommonFieldsSerializer):
    class Meta:
        model = Perm
        fields = [
            *CommonFieldsSerializer.Meta.fields,
            'name',
            'regex',
        ]


class SimpleRoleSerializer(CommonFieldsSerializer):
    class Meta:
        model = Role
        fields = [
            *CommonFieldsSerializer.Meta.fields,
            'name',
        ]


class SimpleDomainSerializer(CommonFieldsSerializer):
    class Meta:
        model = Domain
        fields = [
            *CommonFieldsSerializer.Meta.fields,
            'name',
            'address',
        ]


class SimpleUserSerializer(CommonFieldsSerializer):
    class Meta:
        model = User
        fields = [
            *CommonFieldsSerializer.Meta.fields,
            'name',
            'username',
            'active',
            'expire',
            'domain_id',
            'role_id',
        ]
