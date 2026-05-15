"""Deprecation tracking for env keys — mark keys as deprecated with optional replacement and reason."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def _deprecate_path(base_dir: str) -> Path:
    return Path(base_dir) / "deprecations.json"


def _load_deprecations(base_dir: str) -> dict:
    path = _deprecate_path(base_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_deprecations(base_dir: str, data: dict) -> None:
    path = _deprecate_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def mark_deprecated(
    key: str,
    base_dir: str,
    reason: str = "",
    replacement: Optional[str] = None,
) -> dict:
    """Mark a key as deprecated, optionally with a reason and replacement key."""
    data = _load_deprecations(base_dir)
    data[key] = {"reason": reason, "replacement": replacement}
    _save_deprecations(base_dir, data)
    return data[key]


def unmark_deprecated(key: str, base_dir: str) -> bool:
    """Remove deprecation marking from a key. Returns True if it existed."""
    data = _load_deprecations(base_dir)
    if key not in data:
        return False
    del data[key]
    _save_deprecations(base_dir, data)
    return True


def is_deprecated(key: str, base_dir: str) -> bool:
    """Return True if the key is marked deprecated."""
    return key in _load_deprecations(base_dir)


def get_deprecation_info(key: str, base_dir: str) -> Optional[dict]:
    """Return deprecation metadata for a key, or None if not deprecated."""
    return _load_deprecations(base_dir).get(key)


def list_deprecated(base_dir: str) -> dict:
    """Return all deprecated keys and their metadata."""
    return _load_deprecations(base_dir)


def check_env_deprecations(env: dict, base_dir: str) -> list[dict]:
    """Check an env dict against the deprecation registry.

    Returns a list of warning dicts for any deprecated keys found in env.
    """
    data = _load_deprecations(base_dir)
    warnings = []
    for key in env:
        if key in data:
            entry = {"key": key, **data[key]}
            warnings.append(entry)
    return warnings
