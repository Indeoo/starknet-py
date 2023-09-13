import argparse
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import base64

from config import PASSWORD


def generate_key(password):
    salt = b'\x87\x12\xac\xa3\x91\xb9\xfe\xb4\x08\x0c\xac\x19\xc6d\x85'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


def decrypt_private_key(encrypted_private_key, args):
    key = generate_key(args.password.encode('utf-8'))
    fernet = Fernet(key)
    decrypted_private_key = fernet.decrypt(encrypted_private_key)
    return decrypted_private_key.decode()


def load_password():
    parser = argparse.ArgumentParser(description='Process arguments.')

    parser.add_argument('--password', type=str, required=False, default=os.environ.get('PASSWORD', PASSWORD),
                        help='a string to be processed')

    return parser.parse_args()
