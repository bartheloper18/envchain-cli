"""Encryption and decryption utilities for envchain vaults."""

import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken


SALT_SIZE = 16
ITERATIONS = 390000


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def generate_salt() -> bytes:
    """Generate a random salt."""
    return os.urandom(SALT_SIZE)


def encrypt(data: str, password: str) -> bytes:
    """Encrypt plaintext data with a password.

    Returns salt + encrypted bytes.
    """
    salt = generate_salt()
    key = derive_key(password, salt)
    f = Fernet(key)
    encrypted = f.encrypt(data.encode())
    return salt + encrypted


def decrypt(token: bytes, password: str) -> str:
    """Decrypt data previously encrypted with `encrypt`.

    Raises ValueError on wrong password or corrupted data.
    """
    salt = token[:SALT_SIZE]
    encrypted = token[SALT_SIZE:]
    key = derive_key(password, salt)
    f = Fernet(key)
    try:
        return f.decrypt(encrypted).decode()
    except InvalidToken as exc:
        raise ValueError("Decryption failed: invalid password or corrupted data.") from exc
