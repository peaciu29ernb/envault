"""expiry.py — Track and enforce key expiry dates for vault entries."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_BASE = Path.home() / ".envault" / "expiry"


def _expiry_path(project: str, base_dir: Path = _DEFAULT_BASE) -> Path:
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / f"{project}.json"


def _load_expiry(project: str, base_dir: Path = _DEFAULT_BASE) -> Dict[str, float]:
    path = _expiry_path(project, base_dir)
    if not path.exists():
        return {}
    with path.open("r") as fh:
        return json.load(fh)


def _save_expiry(project: str, data: Dict[str, float], base_dir: Path = _DEFAULT_BASE) -> None:
    with _expiry_path(project, base_dir).open("w") as fh:
        json.dump(data, fh, indent=2)


def set_expiry(project: str, key: str, expires_at: float, base_dir: Path = _DEFAULT_BASE) -> float:
    """Set an explicit Unix-timestamp expiry for *key* in *project*."""
    data = _load_expiry(project, base_dir)
    data[key] = expires_at
    _save_expiry(project, data, base_dir)
    return expires_at


def set_expiry_in(project: str, key: str, seconds: int, base_dir: Path = _DEFAULT_BASE) -> float:
    """Set expiry *seconds* from now for *key* in *project*."""
    expires_at = time.time() + seconds
    return set_expiry(project, key, expires_at, base_dir)


def get_expiry(project: str, key: str, base_dir: Path = _DEFAULT_BASE) -> Optional[float]:
    """Return the expiry timestamp for *key*, or None if not set."""
    return _load_expiry(project, base_dir).get(key)


def is_expired(project: str, key: str, base_dir: Path = _DEFAULT_BASE) -> bool:
    """Return True if *key* has passed its expiry timestamp."""
    expiry = get_expiry(project, key, base_dir)
    if expiry is None:
        return False
    return time.time() >= expiry


def remove_expiry(project: str, key: str, base_dir: Path = _DEFAULT_BASE) -> bool:
    """Remove expiry for *key*. Returns True if the key was present."""
    data = _load_expiry(project, base_dir)
    if key not in data:
        return False
    del data[key]
    _save_expiry(project, data, base_dir)
    return True


def list_expired(project: str, base_dir: Path = _DEFAULT_BASE) -> List[str]:
    """Return all keys that have already expired."""
    now = time.time()
    return [k for k, ts in _load_expiry(project, base_dir).items() if now >= ts]


def list_expiries(project: str, base_dir: Path = _DEFAULT_BASE) -> Dict[str, float]:
    """Return the full expiry map for *project*."""
    return dict(_load_expiry(project, base_dir))
