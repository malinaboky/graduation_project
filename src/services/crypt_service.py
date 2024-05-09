from cryptography.fernet import Fernet

from src.config import HASH


def encrypt_str(value: str):
    f = Fernet(HASH)
    return f.encrypt(bytes(value, 'UTF-8'))


def decrypt(hash_pass: str):
    f = Fernet(HASH)
    return f.decrypt(hash_pass)
