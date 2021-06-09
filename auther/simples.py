from rest_framework import serializers

from auther import models


class SimpleRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Role
        exclude = ['perms']


class SimplePermSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Perm
        exclude = []


class SimpleDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Domain
        exclude = []


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        exclude = ['password']
