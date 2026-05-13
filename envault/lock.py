"""Lock/unlock support for individual env keys to prevent accidental overwrite."""

import json
import os
from pathlib import Path
from typing import List

_DEFAULT_BASE = Path.home() / ".envault" / "locks"


def _lock_path(project: str, base_dir: Path = _DEFAULT_BASE) -> Path:
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / f"{project}.json"


def _load_locks(project: str, base_dir: Path = _DEFAULT_BASE) -> List[str]:
    path = _lock_path(project, base_dir)
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save_locks(project: str, locks: List[str], base_dir: Path = _DEFAULT_BASE) -> None:
    path = _lock_path(project, base_dir)
    with open(path, "w") as f:
        json.dump(sorted(set(locks)), f, indent=2)


def lock_key(project: str, key: str, base_dir: Path = _DEFAULT_BASE) -> List[str]:
    """Lock a key so it cannot be overwritten. Returns updated lock list."""
    locks = _load_locks(project, base_dir)
    if key not in locks:
        locks.append(key)
    _save_locks(project, locks, base_dir)
    return sorted(set(locks))


def unlock_key(project: str, key: str, base_dir: Path = _DEFAULT_BASE) -> bool:
    """Unlock a key. Returns True if key was locked, False if it wasn't."""
    locks = _load_locks(project, base_dir)
    if key not in locks:
        return False
    locks.remove(key)
    _save_locks(project, locks, base_dir)
    return True


def get_locks(project: str, base_dir: Path = _DEFAULT_BASE) -> List[str]:
    """Return all locked keys for a project."""
    return _load_locks(project, base_dir)


def is_locked(project: str, key: str, base_dir: Path = _DEFAULT_BASE) -> bool:
    """Return True if the given key is locked for the project."""
    return key in _load_locks(project, base_dir)


def assert_not_locked(
    project: str, key: str, base_dir: Path = _DEFAULT_BASE
) -> None:
    """Raise ValueError if key is locked."""
    if is_locked(project, key, base_dir):
        raise ValueError(f"Key '{key}' is locked in project '{project}' and cannot be modified.")


def clear_locks(project: str, base_dir: Path = _DEFAULT_BASE) -> None:
    """Remove all locks for a project."""
    path = _lock_path(project, base_dir)
    if path.exists():
        path.unlink()
