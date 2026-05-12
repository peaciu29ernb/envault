"""TTL (time-to-live) support for vault keys — mark keys as expiring and check staleness."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_BASE = Path.home() / ".envault" / "ttl"


def _ttl_path(project: str, base_dir: Path = _DEFAULT_BASE) -> Path:
    return base_dir / f"{project}.json"


def _load_ttl(project: str, base_dir: Path = _DEFAULT_BASE) -> Dict[str, float]:
    path = _ttl_path(project, base_dir)
    if not path.exists():
        return {}
    with path.open("r") as f:
        return json.load(f)


def _save_ttl(project: str, data: Dict[str, float], base_dir: Path = _DEFAULT_BASE) -> None:
    path = _ttl_path(project, base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def set_ttl(project: str, key: str, ttl_seconds: float, base_dir: Path = _DEFAULT_BASE) -> float:
    """Set a TTL for *key* in *project*. Returns the absolute expiry timestamp."""
    data = _load_ttl(project, base_dir)
    expires_at = time.time() + ttl_seconds
    data[key] = expires_at
    _save_ttl(project, data, base_dir)
    return expires_at


def get_expiry(project: str, key: str, base_dir: Path = _DEFAULT_BASE) -> Optional[float]:
    """Return the expiry timestamp for *key*, or None if no TTL is set."""
    data = _load_ttl(project, base_dir)
    return data.get(key)


def is_expired(project: str, key: str, base_dir: Path = _DEFAULT_BASE) -> bool:
    """Return True if *key* has a TTL set and it has passed."""
    expiry = get_expiry(project, key, base_dir)
    if expiry is None:
        return False
    return time.time() >= expiry


def remove_ttl(project: str, key: str, base_dir: Path = _DEFAULT_BASE) -> bool:
    """Remove the TTL entry for *key*. Returns True if it existed."""
    data = _load_ttl(project, base_dir)
    if key not in data:
        return False
    del data[key]
    _save_ttl(project, data, base_dir)
    return True


def expired_keys(project: str, base_dir: Path = _DEFAULT_BASE) -> List[str]:
    """Return a list of keys whose TTL has expired."""
    data = _load_ttl(project, base_dir)
    now = time.time()
    return [k for k, exp in data.items() if now >= exp]


def list_ttl(project: str, base_dir: Path = _DEFAULT_BASE) -> Dict[str, float]:
    """Return all TTL entries for *project* as {key: expiry_timestamp}."""
    return dict(_load_ttl(project, base_dir))
