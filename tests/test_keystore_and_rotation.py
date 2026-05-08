"""Tests for keystore.py and rotation.py."""

import pytest
from pathlib import Path

from envault.crypto import generate_key
from envault.keystore import store_key, retrieve_key, delete_key, list_projects
from envault.vault import create_vault, save_vault, open_vault, load_vault
from envault.rotation import rotate_key, rotate_password


SAMPLE_ENV = {"APP_ENV": "production", "API_KEY": "abc123"}


# --- Keystore tests ---

def test_store_and_retrieve_key(tmp_path):
    ks = tmp_path / ".envault_keys"
    key = generate_key()
    store_key("myproject", key, keystore_path=ks)
    retrieved = retrieve_key("myproject", keystore_path=ks)
    assert retrieved == key


def test_retrieve_missing_key_raises(tmp_path):
    ks = tmp_path / ".envault_keys"
    with pytest.raises(KeyError):
        retrieve_key("nonexistent", keystore_path=ks)


def test_delete_key(tmp_path):
    ks = tmp_path / ".envault_keys"
    key = generate_key()
    store_key("proj", key, keystore_path=ks)
    result = delete_key("proj", keystore_path=ks)
    assert result is True
    with pytest.raises(KeyError):
        retrieve_key("proj", keystore_path=ks)


def test_delete_missing_key_returns_false(tmp_path):
    ks = tmp_path / ".envault_keys"
    result = delete_key("ghost", keystore_path=ks)
    assert result is False


def test_list_projects(tmp_path):
    ks = tmp_path / ".envault_keys"
    store_key("alpha", generate_key(), keystore_path=ks)
    store_key("beta", generate_key(), keystore_path=ks)
    projects = list_projects(keystore_path=ks)
    assert set(projects) == {"alpha", "beta"}


# --- Rotation tests ---

def test_rotate_key_changes_key(tmp_path):
    ks = tmp_path / ".envault_keys"
    vault_file = tmp_path / ".env.vault"

    old_key = generate_key()
    vault_data, _ = create_vault(SAMPLE_ENV, key=old_key)
    save_vault(vault_data, path=vault_file)
    store_key("testproject", old_key, keystore_path=ks)

    new_key = rotate_key("testproject", vault_path=vault_file, keystore_path=ks)

    assert new_key != old_key
    retrieved = retrieve_key("testproject", keystore_path=ks)
    assert retrieved == new_key


def test_rotate_key_vault_still_decryptable(tmp_path):
    ks = tmp_path / ".envault_keys"
    vault_file = tmp_path / ".env.vault"

    old_key = generate_key()
    vault_data, _ = create_vault(SAMPLE_ENV, key=old_key)
    save_vault(vault_data, path=vault_file)
    store_key("myapp", old_key, keystore_path=ks)

    new_key = rotate_key("myapp", vault_path=vault_file, keystore_path=ks)
    reloaded = load_vault(path=vault_file)
    result = open_vault(reloaded, key=new_key)
    assert result == SAMPLE_ENV


def test_rotate_password(tmp_path):
    vault_file = tmp_path / ".env.vault"
    vault_data, _ = create_vault(SAMPLE_ENV, password="oldpass")
    save_vault(vault_data, path=vault_file)

    rotate_password("myapp", "oldpass", "newpass", vault_path=vault_file)

    reloaded = load_vault(path=vault_file)
    result = open_vault(reloaded, password="newpass")
    assert result == SAMPLE_ENV
