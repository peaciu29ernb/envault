"""Tests for vault.py: create, save, load, and open vault operations."""

import json
import pytest
from pathlib import Path

from envault.crypto import generate_key
from envault.vault import (
    _parse_env_string,
    _serialize_env_dict,
    create_vault,
    save_vault,
    load_vault,
    open_vault,
)


SAMPLE_ENV = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "mysecret"}


def test_parse_env_string_basic():
    env_str = "DB_HOST=localhost\nDB_PORT=5432\n# comment\n"
    result = _parse_env_string(env_str)
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_serialize_env_dict_roundtrip():
    serialized = _serialize_env_dict(SAMPLE_ENV)
    parsed = _parse_env_string(serialized)
    assert parsed == SAMPLE_ENV


def test_create_vault_with_key():
    key = generate_key()
    vault_data, returned_key = create_vault(SAMPLE_ENV, key=key)
    assert vault_data["mode"] == "key"
    assert vault_data["version"] == 1
    assert "data" in vault_data
    assert returned_key == key


def test_create_vault_generates_key_if_none():
    vault_data, returned_key = create_vault(SAMPLE_ENV)
    assert len(returned_key) > 0
    assert vault_data["mode"] == "key"


def test_create_vault_with_password():
    vault_data, returned_key = create_vault(SAMPLE_ENV, password="strongpass")
    assert vault_data["mode"] == "password"
    assert returned_key == b""


def test_open_vault_with_key_roundtrip():
    key = generate_key()
    vault_data, _ = create_vault(SAMPLE_ENV, key=key)
    result = open_vault(vault_data, key=key)
    assert result == SAMPLE_ENV


def test_open_vault_with_password_roundtrip():
    vault_data, _ = create_vault(SAMPLE_ENV, password="testpassword")
    result = open_vault(vault_data, password="testpassword")
    assert result == SAMPLE_ENV


def test_open_vault_missing_key_raises():
    vault_data, _ = create_vault(SAMPLE_ENV)
    with pytest.raises(ValueError, match="Key required"):
        open_vault(vault_data)


def test_open_vault_missing_password_raises():
    vault_data, _ = create_vault(SAMPLE_ENV, password="pw")
    with pytest.raises(ValueError, match="Password required"):
        open_vault(vault_data)


def test_save_and_load_vault(tmp_path):
    key = generate_key()
    vault_data, _ = create_vault(SAMPLE_ENV, key=key)
    vault_file = tmp_path / ".env.vault"
    save_vault(vault_data, path=vault_file)
    assert vault_file.exists()
    loaded = load_vault(path=vault_file)
    assert loaded == vault_data


def test_load_vault_not_found_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_vault(path=tmp_path / "nonexistent.vault")
