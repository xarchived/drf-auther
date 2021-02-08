from django.db import models

from fancy.models import FancyModel


class Domain(FancyModel):
    name = models.TextField(unique=True, null=False)
    address = models.TextField(unique=True, null=False)


class Perm(FancyModel):
    name = models.TextField(null=True, unique=True)
    regex = models.TextField(null=False, unique=True)


class Role(FancyModel):
    name = models.TextField(unique=True, null=False)
    perms = models.ManyToManyField(Perm, related_name='roles')


class User(FancyModel):
    name = models.TextField(null=True)
    username = models.TextField(unique=True, null=False, max_length=64)
    password = models.TextField(null=False, max_length=64)
    avatar_token = models.TextField(null=True)
    active = models.BooleanField(null=False, default=True)
    expire = models.DateTimeField(null=True)
    domain = models.ForeignKey(Domain, on_delete=models.RESTRICT, related_name='users', null=True)
    role = models.ForeignKey(Role, on_delete=models.RESTRICT, related_name='users', null=True)
