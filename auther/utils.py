import secrets
import string

import bcrypt

from auther.models import User


def generate_otp(length: int) -> str:
    numbers = string.digits
    otp = ''.join(secrets.choice(numbers) for _ in range(length))
    return otp


def generate_password(length: int) -> str:
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def generate_token() -> str:
    return secrets.token_urlsafe(48)  # 64 characters


def hash_password(password: str) -> str:
    return str(bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()), 'utf-8')


def check_password(password: str, hashed_password: str) -> bool:
    if bcrypt.checkpw(bytes(password, encoding='utf-8'), bytes(hashed_password, encoding='utf-8')):
        return True

    return False


def user_to_dict(user: User) -> dict:
    return {
        'id': user.id,
        'name': user.name,
        'username': user.name,
        'domain': user.domain.name if user.domain else None,
        'roles': [role.name for role in user.roles.order_by('-level')],
    }
