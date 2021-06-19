import secrets
import string

import bcrypt


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
