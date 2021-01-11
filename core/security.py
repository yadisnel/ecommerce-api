import random
import re

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def generate_security_code_for_email():
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    security_code = ''.join(random.choice(alphabet) for i in range(64))
    return security_code


def generate_security_code_for_phone():
    alphabet = "0123456789"
    security_code = ''.join(random.choice(alphabet) for i in range(6))
    return security_code


def is_strong_password(password: str)-> bool:
    if len(password) < 8:
        return False
    elif not re.search("[a-z]", password):
        return False
    elif not re.search("[A-Z]", password):
        return False
    elif not re.search("[0-9]", password):
        return False
    else:
        return True
