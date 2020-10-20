import random
import string

import bcrypt


def generate_random_string(length: int) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def generate_password(length: int) -> str:
    return generate_random_string(length)


def generate_token() -> str:
    return generate_random_string(53)


def hash_password(password: bytes) -> bytes:
    return bcrypt.hashpw(password, bcrypt.gensalt())


def check_password(password: str, hashed_password: str) -> bool:
    if bcrypt.checkpw(bytes(password, encoding='utf-8'), bytes(hashed_password, encoding='utf-8')):
        return True

    return False
