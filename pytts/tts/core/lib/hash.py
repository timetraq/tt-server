"""
Stuff around creating Hashes and Salts
"""

from base64 import b64encode, b64decode
from hashlib import sha512
from random import SystemRandom


def create_salt() -> bytes:
    """
    Create a Salt in Bytes

    :return: Salt data
    :rtype: bytes
    """
    rand = SystemRandom()
    salt_bytes = []
    while len(salt_bytes) < 64:
        salt_bytes.append(rand.randint(0, 255))
    return bytes(salt_bytes)


def create_salt_as_base64_string() -> str:
    """
    Create a Salt as String

    :return: Base 64 encoded String representing a salt
    :rtype: str
    """
    return b64encode(create_salt()).decode('utf-8')


def hash_password_with_salt(password: str, salt: bytes) -> bytes:
    """
    Hash a password with a salt (250000 rounds)

    :param str password: Password to hash
    :param bytes salt: Salt
    :return: Hash in bytes
    :rtype: bytes
    """
    load = password.encode('utf-8')
    for dummy in range(250000):
        load += salt
        load = sha512(load).digest()
    return load


def hash_password_with_base64_salt_as_base64_string(password: str, salt: str) -> str:
    """
    Hash a password and use a base64 salt and deliver a base64 string as result

    :param str password: Password to hash
    :param str salt: Salt
    :return: Base 64 encoded salted hash of password
    :rtype: str
    """
    decoded_salt = b64decode(salt)
    return b64encode(hash_password_with_salt(password, decoded_salt)).decode('utf-8')
