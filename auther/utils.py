import secrets
import string

import bcrypt


def generate_password(length: int) -> bytes:
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return bytes(password, encoding='ascii')


def generate_token() -> str:
    return secrets.token_urlsafe(53)


def hash_password(password: bytes) -> bytes:
    return bcrypt.hashpw(password, bcrypt.gensalt())


def check_password(password: str, hashed_password: str) -> bool:
    if bcrypt.checkpw(bytes(password, encoding='utf-8'), bytes(hashed_password, encoding='utf-8')):
        return True

    return False
