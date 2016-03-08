"""
Token Stuff
"""

from random import SystemRandom
from string import ascii_letters, digits


TOKEN_CHARS = ascii_letters + digits


def token_generator() -> str:
    """
    Create a token

    :return: A token
    :rtype: str
    """
    rand = SystemRandom()
    token = ''
    while len(token) < 64:
        token += TOKEN_CHARS[rand.randrange(len(TOKEN_CHARS))]
    return token
