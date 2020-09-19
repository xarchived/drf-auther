from django.db import models


class Domain(models.Model):
    name = models.TextField(unique=True, null=False)
    address = models.TextField(unique=True, null=False)


class Perm(models.Model):
    method = models.TextField(null=False)
    path = models.TextField(null=False)

    class Meta:
        unique_together = ['method', 'path']


class Role(models.Model):
    name = models.TextField(unique=True, null=False)
    perms = models.ManyToManyField(Perm, related_name='roles')


class User(models.Model):
    name = models.TextField(null=False)
    username = models.TextField(unique=True, null=False)
    password = models.BinaryField(null=False)
    avatar_pic = models.TextField(null=True)
    domain = models.ForeignKey(Domain, on_delete=models.RESTRICT, related_name='users', null=True)
    roles = models.ManyToManyField(Role, related_name='users')
