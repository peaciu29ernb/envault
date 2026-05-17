"""Tests for envault.encrypt_field (per-field encryption)."""

import pytest

from envault.crypto import generate_key
from envault.encrypt_field import (
    FIELD_PREFIX,
    FieldEncryptError,
    decrypt_field,
    decrypt_fields,
    encrypt_field,
    encrypt_fields,
    is_encrypted_field,
    list_encrypted_keys,
)


@pytest.fixture()
def key() -> bytes:
    return generate_key()


def test_encrypt_field_returns_prefixed_string(key):
    result = encrypt_field("secret", key)
    assert result.startswith(FIELD_PREFIX)


def test_encrypt_decrypt_field_roundtrip(key):
    original = "my_secret_value"
    encrypted = encrypt_field(original, key)
    assert decrypt_field(encrypted, key) == original


def test_decrypt_field_wrong_key_raises(key):
    wrong_key = generate_key()
    encrypted = encrypt_field("value", key)
    with pytest.raises(FieldEncryptError):
        decrypt_field(encrypted, wrong_key)


def test_decrypt_field_not_encrypted_raises(key):
    with pytest.raises(FieldEncryptError, match="not encrypted"):
        decrypt_field("plaintext", key)


def test_is_encrypted_field_true(key):
    enc = encrypt_field("val", key)
    assert is_encrypted_field(enc) is True


def test_is_encrypted_field_false():
    assert is_encrypted_field("plain") is False
    assert is_encrypted_field("") is False


def test_encrypt_fields_encrypts_specified_keys(key):
    env = {"DB_PASS": "secret", "APP_HOST": "localhost"}
    result = encrypt_fields(env, ["DB_PASS"], key)
    assert is_encrypted_field(result["DB_PASS"])
    assert result["APP_HOST"] == "localhost"


def test_encrypt_fields_missing_key_raises(key):
    env = {"A": "1"}
    with pytest.raises(FieldEncryptError, match="not found"):
        encrypt_fields(env, ["MISSING"], key)


def test_encrypt_fields_already_encrypted_skips(key):
    env = {"TOKEN": encrypt_field("abc", key)}
    result = encrypt_fields(env, ["TOKEN"], key)
    # Should still decrypt correctly (not double-encrypted)
    assert decrypt_field(result["TOKEN"], key) == "abc"


def test_decrypt_fields_all_encrypted_keys(key):
    env = {
        "DB_PASS": encrypt_field("hunter2", key),
        "API_KEY": encrypt_field("xyz123", key),
        "HOST": "localhost",
    }
    result = decrypt_fields(env, key)
    assert result["DB_PASS"] == "hunter2"
    assert result["API_KEY"] == "xyz123"
    assert result["HOST"] == "localhost"


def test_decrypt_fields_specific_keys_only(key):
    env = {
        "A": encrypt_field("alpha", key),
        "B": encrypt_field("beta", key),
    }
    result = decrypt_fields(env, key, keys=["A"])
    assert result["A"] == "alpha"
    assert is_encrypted_field(result["B"])  # B still encrypted


def test_list_encrypted_keys(key):
    env = {
        "SECRET": encrypt_field("s", key),
        "PLAIN": "visible",
        "TOKEN": encrypt_field("t", key),
    }
    result = list_encrypted_keys(env)
    assert set(result) == {"SECRET", "TOKEN"}


def test_list_encrypted_keys_empty_env():
    assert list_encrypted_keys({}) == []
