"""Vault file management: read/write encrypted .env.vault files."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

from envault.crypto import encrypt, decrypt, generate_key, encrypt_with_password, decrypt_with_password

VAULT_FILENAME = ".env.vault"
DEFAULT_ENCODING = "utf-8"


def _parse_env_string(env_string: str) -> Dict[str, str]:
    """Parse a .env formatted string into a dictionary."""
    result = {}
    for line in env_string.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip()
    return result


def _serialize_env_dict(env_dict: Dict[str, str]) -> str:
    """Serialize a dictionary to .env formatted string."""
    lines = []
    for key, value in env_dict.items():
        lines.append(f"{key}={value}")
    return "\n".join(lines)


def create_vault(
    env_dict: Dict[str, str],
    password: Optional[str] = None,
    key: Optional[bytes] = None,
) -> tuple[dict, bytes]:
    """Encrypt env dict and return vault metadata + key."""
    if password is None and key is None:
        key = generate_key()

    plaintext = _serialize_env_dict(env_dict).encode(DEFAULT_ENCODING)

    if password:
        ciphertext = encrypt_with_password(plaintext, password)
        vault_data = {"version": 1, "mode": "password", "data": ciphertext.hex()}
        return vault_data, b""
    else:
        ciphertext = encrypt(plaintext, key)
        vault_data = {"version": 1, "mode": "key", "data": ciphertext.hex()}
        return vault_data, key


def save_vault(vault_data: dict, path: Optional[Path] = None) -> Path:
    """Write vault data as JSON to disk."""
    vault_path = path or Path(VAULT_FILENAME)
    vault_path.write_text(json.dumps(vault_data, indent=2), encoding=DEFAULT_ENCODING)
    return vault_path


def load_vault(path: Optional[Path] = None) -> dict:
    """Load vault data from disk."""
    vault_path = path or Path(VAULT_FILENAME)
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault file not found: {vault_path}")
    return json.loads(vault_path.read_text(encoding=DEFAULT_ENCODING))


def open_vault(
    vault_data: dict,
    password: Optional[str] = None,
    key: Optional[bytes] = None,
) -> Dict[str, str]:
    """Decrypt vault data and return env dict."""
    mode = vault_data.get("mode")
    ciphertext = bytes.fromhex(vault_data["data"])

    if mode == "password":
        if password is None:
            raise ValueError("Password required to open this vault.")
        plaintext = decrypt_with_password(ciphertext, password)
    elif mode == "key":
        if key is None:
            raise ValueError("Key required to open this vault.")
        plaintext = decrypt(ciphertext, key)
    else:
        raise ValueError(f"Unknown vault mode: {mode}")

    return _parse_env_string(plaintext.decode(DEFAULT_ENCODING))
