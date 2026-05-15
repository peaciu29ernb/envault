"""Immutable key registry — keys marked immutable cannot be modified or deleted."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

_DEFAULT_BASE = Path.home() / ".envault" / "immutable"


def _immutable_path(project: str, base_dir: Path = _DEFAULT_BASE) -> Path:
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / f"{project}.json"


def _load_immutable(project: str, base_dir: Path = _DEFAULT_BASE) -> List[str]:
    path = _immutable_path(project, base_dir)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_immutable(project: str, keys: List[str], base_dir: Path = _DEFAULT_BASE) -> None:
    path = _immutable_path(project, base_dir)
    path.write_text(json.dumps(sorted(set(keys))))


def mark_immutable(project: str, key: str, base_dir: Path = _DEFAULT_BASE) -> List[str]:
    """Mark *key* as immutable for *project*. Returns updated list."""
    keys = _load_immutable(project, base_dir)
    if key not in keys:
        keys.append(key)
    _save_immutable(project, keys, base_dir)
    return sorted(set(keys))


def unmark_immutable(project: str, key: str, base_dir: Path = _DEFAULT_BASE) -> bool:
    """Remove immutable mark from *key*. Returns True if it was present."""
    keys = _load_immutable(project, base_dir)
    if key not in keys:
        return False
    keys.remove(key)
    _save_immutable(project, keys, base_dir)
    return True


def is_immutable(project: str, key: str, base_dir: Path = _DEFAULT_BASE) -> bool:
    """Return True if *key* is marked immutable for *project*."""
    return key in _load_immutable(project, base_dir)


def get_immutable_keys(project: str, base_dir: Path = _DEFAULT_BASE) -> List[str]:
    """Return all immutable keys for *project*."""
    return _load_immutable(project, base_dir)


def assert_mutable(project: str, key: str, base_dir: Path = _DEFAULT_BASE) -> None:
    """Raise ValueError if *key* is immutable for *project*."""
    if is_immutable(project, key, base_dir):
        raise ValueError(f"Key '{key}' is immutable for project '{project}' and cannot be modified.")
