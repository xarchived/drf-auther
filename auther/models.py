from django.db.models import (
    TextField,
    ManyToManyField,
    BooleanField,
    DateTimeField,
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

    @property
    def as_simple_dict(self) -> dict:
        # noinspection PyUnresolvedReferences
        return {
            'id': self.id,
            'name': self.name,
            'username': self.name,
            'domain': self.domain.name if self.domain else None,
            'roles': [role.name for role in self.roles.all().order_by('-level')],
        }


class Session(SafeDeleteModel, LogFieldsModel):
    token = TextField(unique=True, max_length=64)
    user = ForeignKey(User, on_delete=RESTRICT, related_name='sessions')
    user_agent = TextField(max_length=200)
