"""Tests for envault.crypto encryption/decryption utilities."""

import pytest
from cryptography.fernet import InvalidToken

from envault.crypto import (
    generate_key,
    encrypt,
    decrypt,
    derive_key,
    encrypt_with_password,
    decrypt_with_password,
)


SAMPLE_TEXT = "DATABASE_URL=postgres://user:pass@localhost/mydb\nSECRET_KEY=supersecret"
SAMPLE_PASSWORD = "correct-horse-battery-staple"


def test_generate_key_returns_bytes():
    key = generate_key()
    assert isinstance(key, bytes)
    assert len(key) == 44  # base64-encoded 32-byte Fernet key


def test_encrypt_returns_bytes():
    key = generate_key()
    ciphertext = encrypt(SAMPLE_TEXT, key)
    assert isinstance(ciphertext, bytes)
    assert ciphertext != SAMPLE_TEXT.encode()


def test_encrypt_decrypt_roundtrip():
    key = generate_key()
    ciphertext = encrypt(SAMPLE_TEXT, key)
    result = decrypt(ciphertext, key)
    assert result == SAMPLE_TEXT


def test_decrypt_wrong_key_raises():
    key1 = generate_key()
    key2 = generate_key()
    ciphertext = encrypt(SAMPLE_TEXT, key1)
    with pytest.raises(InvalidToken):
        decrypt(ciphertext, key2)


def test_derive_key_deterministic():
    salt = b"\x00" * 16
    key1 = derive_key(SAMPLE_PASSWORD, salt)
    key2 = derive_key(SAMPLE_PASSWORD, salt)
    assert key1 == key2


def test_derive_key_different_salts():
    import os
    salt1 = os.urandom(16)
    salt2 = os.urandom(16)
    key1 = derive_key(SAMPLE_PASSWORD, salt1)
    key2 = derive_key(SAMPLE_PASSWORD, salt2)
    assert key1 != key2


def test_encrypt_with_password_returns_payload():
    payload = encrypt_with_password(SAMPLE_TEXT, SAMPLE_PASSWORD)
    assert "salt" in payload
    assert "ciphertext" in payload
    assert isinstance(payload["salt"], str)
    assert isinstance(payload["ciphertext"], str)


def test_password_roundtrip():
    payload = encrypt_with_password(SAMPLE_TEXT, SAMPLE_PASSWORD)
    result = decrypt_with_password(payload, SAMPLE_PASSWORD)
    assert result == SAMPLE_TEXT


def test_wrong_password_raises():
    payload = encrypt_with_password(SAMPLE_TEXT, SAMPLE_PASSWORD)
    with pytest.raises(InvalidToken):
        decrypt_with_password(payload, "wrong-password")


def test_each_encryption_produces_unique_ciphertext():
    key = generate_key()
    ct1 = encrypt(SAMPLE_TEXT, key)
    ct2 = encrypt(SAMPLE_TEXT, key)
    # Fernet uses a random IV, so ciphertexts should differ
    assert ct1 != ct2
