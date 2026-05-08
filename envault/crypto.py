"""Core encryption/decryption utilities for envault using Fernet symmetric encryption."""

import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


SALT_SIZE = 16
ITERATIONS = 390_000


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a password and salt using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    raw_key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(raw_key)


def generate_key() -> bytes:
    """Generate a new random Fernet key."""
    return Fernet.generate_key()


def encrypt(plaintext: str, key: bytes) -> bytes:
    """Encrypt a plaintext string and return the ciphertext bytes."""
    f = Fernet(key)
    return f.encrypt(plaintext.encode())


def decrypt(ciphertext: bytes, key: bytes) -> str:
    """Decrypt ciphertext bytes and return the plaintext string.

    Raises:
        InvalidToken: if the key is wrong or data is corrupted.
    """
    f = Fernet(key)
    return f.decrypt(ciphertext).decode()


def encrypt_with_password(plaintext: str, password: str) -> dict:
    """Encrypt plaintext using a password-derived key.

    Returns a dict with 'salt' and 'ciphertext' as hex strings.
    """
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    ciphertext = encrypt(plaintext, key)
    return {
        "salt": salt.hex(),
        "ciphertext": ciphertext.decode(),
    }


def decrypt_with_password(payload: dict, password: str) -> str:
    """Decrypt a payload produced by encrypt_with_password.

    Raises:
        InvalidToken: if the password is incorrect or data is tampered.
    """
    salt = bytes.fromhex(payload["salt"])
    key = derive_key(password, salt)
    return decrypt(payload["ciphertext"].encode(), key)
