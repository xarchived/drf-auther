from django.db.models import (
    TextField,
    ManyToManyField,
    BooleanField,
    DateTimeField,
    FloatField,
    IntegerField,
    ForeignKey,
    RESTRICT,
    EmailField,
    BigIntegerField,
)

from fancy.models import SafeDeleteModel, LogFieldsModel


class Perm(SafeDeleteModel, LogFieldsModel):
    name = TextField(null=True, unique=True)
    regex = TextField(null=False, unique=True)


class Role(SafeDeleteModel, LogFieldsModel):
    name = TextField(unique=True, null=False)
    perms = ManyToManyField(Perm, related_name='roles')
    level = IntegerField(null=False, default=0)
    child_limit = IntegerField(null=True)


class Domain(SafeDeleteModel, LogFieldsModel):
    name = TextField(unique=True, null=False)
    address = TextField(unique=True, null=False)


class User(SafeDeleteModel, LogFieldsModel):
    name = TextField(null=True)
    username = TextField(unique=True, null=True, max_length=64)
    email = EmailField(unique=True, null=True, max_length=320)
    phone = BigIntegerField(unique=True, null=True)
    password = TextField(null=False, max_length=64)
    active = BooleanField(null=False, default=True)
    expire = DateTimeField(null=True)
    domain = ForeignKey(Domain, on_delete=RESTRICT, related_name='users', null=True)
    parent = ForeignKey('self', on_delete=RESTRICT, related_name='children', null=True)
    roles = ManyToManyField(Role, related_name='users')
    manager_name = TextField(null=True)
    latitude = FloatField(null=True, db_index=True)
    longitude = FloatField(null=True, db_index=True)
    legal_entity = BooleanField(default=False, null=True)
    natural_person = BooleanField(default=False, null=True)
    vip = BooleanField(default=False, null=True)


class Session(SafeDeleteModel, LogFieldsModel):
    token = TextField(unique=True, max_length=64)
    user = ForeignKey(User, on_delete=RESTRICT, related_name='sessions')
    user_agent = TextField(max_length=200)
