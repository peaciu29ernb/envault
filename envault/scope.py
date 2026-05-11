"""Scope management: associate env keys with named scopes (e.g. dev, prod, ci)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _scope_path(base_dir: str, project: str) -> Path:
    return Path(base_dir) / f"{project}.scopes.json"


def _load_scopes(path: Path) -> Dict[str, List[str]]:
    """Return mapping of scope -> list of keys."""
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_scopes(path: Path, data: Dict[str, List[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def add_to_scope(base_dir: str, project: str, scope: str, key: str) -> List[str]:
    """Add *key* to *scope*. Returns updated key list for that scope."""
    path = _scope_path(base_dir, project)
    data = _load_scopes(path)
    keys = data.setdefault(scope, [])
    if key not in keys:
        keys.append(key)
    _save_scopes(path, data)
    return list(keys)


def remove_from_scope(base_dir: str, project: str, scope: str, key: str) -> bool:
    """Remove *key* from *scope*. Returns True if removed, False if not found."""
    path = _scope_path(base_dir, project)
    data = _load_scopes(path)
    keys = data.get(scope, [])
    if key not in keys:
        return False
    keys.remove(key)
    data[scope] = keys
    _save_scopes(path, data)
    return True


def get_scope_keys(base_dir: str, project: str, scope: str) -> List[str]:
    """Return all keys belonging to *scope*."""
    path = _scope_path(base_dir, project)
    data = _load_scopes(path)
    return list(data.get(scope, []))


def list_scopes(base_dir: str, project: str) -> List[str]:
    """Return all scope names for *project*."""
    path = _scope_path(base_dir, project)
    data = _load_scopes(path)
    return sorted(data.keys())


def key_scopes(base_dir: str, project: str, key: str) -> List[str]:
    """Return all scopes that contain *key*."""
    path = _scope_path(base_dir, project)
    data = _load_scopes(path)
    return sorted(scope for scope, keys in data.items() if key in keys)


def filter_env_by_scope(
    base_dir: str, project: str, scope: str, env: Dict[str, str]
) -> Dict[str, str]:
    """Return a subset of *env* containing only keys in *scope*."""
    allowed = set(get_scope_keys(base_dir, project, scope))
    return {k: v for k, v in env.items() if k in allowed}
