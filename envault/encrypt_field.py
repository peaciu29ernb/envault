"""Per-field encryption: selectively encrypt individual env values."""

from __future__ import annotations

import json
from typing import Dict, List, Optional, Tuple

from envault.crypto import encrypt, decrypt, generate_key

FIELD_PREFIX = "enc:"


class FieldEncryptError(Exception):
    pass


def encrypt_field(value: str, key: bytes) -> str:
    """Encrypt a single env value; returns a prefixed base64-like token."""
    token = encrypt(value.encode(), key)
    return FIELD_PREFIX + token


def decrypt_field(value: str, key: bytes) -> str:
    """Decrypt a single encrypted env value."""
    if not value.startswith(FIELD_PREFIX):
        raise FieldEncryptError(f"Value is not encrypted (missing prefix '{FIELD_PREFIX}')")
    token = value[len(FIELD_PREFIX):]
    try:
        return decrypt(token, key).decode()
    except Exception as exc:
        raise FieldEncryptError(f"Failed to decrypt field: {exc}") from exc


def is_encrypted_field(value: str) -> bool:
    """Return True if the value looks like a per-field encrypted token."""
    return isinstance(value, str) and value.startswith(FIELD_PREFIX)


def encrypt_fields(env: Dict[str, str], keys: List[str], key: bytes) -> Dict[str, str]:
    """Return a new env dict with the specified keys encrypted."""
    result = dict(env)
    for k in keys:
        if k not in result:
            raise FieldEncryptError(f"Key '{k}' not found in env")
        if is_encrypted_field(result[k]):
            continue  # already encrypted, skip
        result[k] = encrypt_field(result[k], key)
    return result


def decrypt_fields(
    env: Dict[str, str],
    key: bytes,
    keys: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Return a new env dict with all (or specified) encrypted fields decrypted."""
    result = dict(env)
    targets = keys if keys is not None else list(result.keys())
    for k in targets:
        if k in result and is_encrypted_field(result[k]):
            result[k] = decrypt_field(result[k], key)
    return result


def list_encrypted_keys(env: Dict[str, str]) -> List[str]:
    """Return the list of keys whose values are currently encrypted."""
    return [k for k, v in env.items() if is_encrypted_field(v)]
