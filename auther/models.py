from django.db.models import (
    TextField,
    ManyToManyField,
    BooleanField,
    DateTimeField,
    ForeignKey,
    Model,
    RESTRICT,
)

from fancy.models import SafeDeleteModel, LogFieldsModel


class Perm(SafeDeleteModel, LogFieldsModel):
    name = TextField(null=True, unique=True)
    regex = TextField(null=False, unique=True)


class Role(SafeDeleteModel, LogFieldsModel):
    name = TextField(unique=True, null=False)
    perms = ManyToManyField(Perm, related_name='roles')


class Domain(SafeDeleteModel, LogFieldsModel):
    name = TextField(unique=True, null=False)
    address = TextField(unique=True, null=False)


class User(SafeDeleteModel, LogFieldsModel):
    name = TextField(null=True)
    username = TextField(unique=True, null=False, max_length=64)
    password = TextField(null=False, max_length=64)
    avatar_token = TextField(null=True)
    active = BooleanField(null=False, default=True)
    expire = DateTimeField(null=True)
    domain = ForeignKey(Domain, on_delete=RESTRICT, related_name='users', null=True)
    role = ForeignKey(Role, on_delete=RESTRICT, related_name='users', null=True)


class Session(Model):
    token = TextField(unique=True, max_length=64)
    user = ForeignKey(User, on_delete=RESTRICT, related_name='sessions')
    user_agent = TextField(max_length=200)
    inserted_at = DateTimeField(auto_now_add=True)
