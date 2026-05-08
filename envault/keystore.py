"""Keystore: persist and retrieve encryption keys for vaults."""

import json
import os
from pathlib import Path
from typing import Optional

KEYSTORE_FILENAME = ".envault_keys"
DEFAULT_ENCODING = "utf-8"


def _default_keystore_path() -> Path:
    """Return the default keystore path in user home directory."""
    return Path.home() / KEYSTORE_FILENAME


def _load_keystore(keystore_path: Path) -> dict:
    if keystore_path.exists():
        return json.loads(keystore_path.read_text(encoding=DEFAULT_ENCODING))
    return {}


def _save_keystore(data: dict, keystore_path: Path) -> None:
    keystore_path.write_text(json.dumps(data, indent=2), encoding=DEFAULT_ENCODING)
    # Restrict permissions on the keystore file
    try:
        os.chmod(keystore_path, 0o600)
    except OSError:
        pass


def store_key(project_id: str, key: bytes, keystore_path: Optional[Path] = None) -> None:
    """Store a key for a given project identifier."""
    path = keystore_path or _default_keystore_path()
    data = _load_keystore(path)
    data[project_id] = key.hex()
    _save_keystore(data, path)


def retrieve_key(project_id: str, keystore_path: Optional[Path] = None) -> bytes:
    """Retrieve a key for a given project identifier."""
    path = keystore_path or _default_keystore_path()
    data = _load_keystore(path)
    if project_id not in data:
        raise KeyError(f"No key found for project: {project_id}")
    return bytes.fromhex(data[project_id])


def delete_key(project_id: str, keystore_path: Optional[Path] = None) -> bool:
    """Delete a key for a given project. Returns True if deleted, False if not found."""
    path = keystore_path or _default_keystore_path()
    data = _load_keystore(path)
    if project_id in data:
        del data[project_id]
        _save_keystore(data, path)
        return True
    return False


def list_projects(keystore_path: Optional[Path] = None) -> list:
    """List all project IDs in the keystore."""
    path = keystore_path or _default_keystore_path()
    data = _load_keystore(path)
    return list(data.keys())
