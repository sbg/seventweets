import os
import binascii


def generate_api_token():
    """
    Generates random token.
    """
    return binascii.b2a_hex(os.urandom(15)).decode('ascii')
