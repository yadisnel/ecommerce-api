import random

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def generate_security_code_for_email():
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    security_code = ''.join(random.choice(alphabet) for i in range(64))
    return security_code


def generate_security_code_for_phone():
    alphabet = "0123456789"
    security_code = ''.join(random.choice(alphabet) for i in range(6))
    return security_code
