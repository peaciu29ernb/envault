"""Alias support: map short names to environment variable keys."""

import json
from pathlib import Path
from typing import Dict, List, Optional


def _alias_path(base_dir: str = ".envault") -> Path:
    return Path(base_dir) / "aliases.json"


def _load_aliases(base_dir: str = ".envault") -> Dict[str, str]:
    path = _alias_path(base_dir)
    if not path.exists():
        return {}
    with path.open("r") as f:
        return json.load(f)


def _save_aliases(aliases: Dict[str, str], base_dir: str = ".envault") -> None:
    path = _alias_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(aliases, f, indent=2)


def add_alias(alias: str, key: str, base_dir: str = ".envault") -> None:
    """Register an alias pointing to an env key."""
    if not alias or not key:
        raise ValueError("alias and key must be non-empty strings")
    aliases = _load_aliases(base_dir)
    aliases[alias] = key
    _save_aliases(aliases, base_dir)


def remove_alias(alias: str, base_dir: str = ".envault") -> bool:
    """Remove an alias. Returns True if it existed, False otherwise."""
    aliases = _load_aliases(base_dir)
    if alias not in aliases:
        return False
    del aliases[alias]
    _save_aliases(aliases, base_dir)
    return True


def resolve_alias(alias: str, base_dir: str = ".envault") -> Optional[str]:
    """Return the key the alias points to, or None if not found."""
    return _load_aliases(base_dir).get(alias)


def list_aliases(base_dir: str = ".envault") -> Dict[str, str]:
    """Return all registered aliases as {alias: key}."""
    return dict(_load_aliases(base_dir))


def resolve_key(name: str, base_dir: str = ".envault") -> str:
    """Return the canonical key for *name*, resolving alias if needed."""
    resolved = resolve_alias(name, base_dir)
    return resolved if resolved is not None else name


def aliases_for_key(key: str, base_dir: str = ".envault") -> List[str]:
    """Return all aliases that point to *key*."""
    return [a for a, k in _load_aliases(base_dir).items() if k == key]
