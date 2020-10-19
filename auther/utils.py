import random
import string


def generate_random_string(length: int):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def generate_password(length: int):
    return generate_random_string(length)


def generate_token():
    return generate_random_string(53)
