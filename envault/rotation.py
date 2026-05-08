"""Key rotation support: re-encrypt vault data with a new key."""

from pathlib import Path
from typing import Optional

from envault.crypto import generate_key
from envault.vault import create_vault, open_vault, save_vault, load_vault
from envault.keystore import store_key, retrieve_key


def rotate_key(
    project_id: str,
    vault_path: Optional[Path] = None,
    keystore_path: Optional[Path] = None,
) -> bytes:
    """
    Rotate the encryption key for a project vault.

    Loads the existing vault using the current key, re-encrypts it
    with a newly generated key, saves the updated vault, and updates
    the keystore with the new key.

    Returns the new key.
    """
    old_key = retrieve_key(project_id, keystore_path=keystore_path)
    vault_data = load_vault(path=vault_path)

    env_dict = open_vault(vault_data, key=old_key)

    new_key = generate_key()
    new_vault_data, _ = create_vault(env_dict, key=new_key)

    save_vault(new_vault_data, path=vault_path)
    store_key(project_id, new_key, keystore_path=keystore_path)

    return new_key


def rotate_password(
    project_id: str,
    old_password: str,
    new_password: str,
    vault_path: Optional[Path] = None,
) -> None:
    """
    Rotate the password for a password-protected vault.

    Decrypts with the old password and re-encrypts with the new one.
    """
    vault_data = load_vault(path=vault_path)
    env_dict = open_vault(vault_data, password=old_password)

    new_vault_data, _ = create_vault(env_dict, password=new_password)
    save_vault(new_vault_data, path=vault_path)
