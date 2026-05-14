"""Access control: restrict which keys a given role/user can read or write."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_BASE = Path.home() / ".envault" / "access"


def _access_path(project: str, base_dir: Optional[Path] = None) -> Path:
    base = base_dir or _DEFAULT_BASE
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{project}.json"


def _load_access(project: str, base_dir: Optional[Path] = None) -> Dict[str, List[str]]:
    path = _access_path(project, base_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_access(project: str, data: Dict[str, List[str]], base_dir: Optional[Path] = None) -> None:
    path = _access_path(project, base_dir)
    path.write_text(json.dumps(data, indent=2))


def grant_access(project: str, role: str, key: str, base_dir: Optional[Path] = None) -> List[str]:
    """Grant *role* access to *key* in *project*. Returns updated key list for role."""
    data = _load_access(project, base_dir)
    keys = data.setdefault(role, [])
    if key not in keys:
        keys.append(key)
    _save_access(project, data, base_dir)
    return list(keys)


def revoke_access(project: str, role: str, key: str, base_dir: Optional[Path] = None) -> bool:
    """Revoke *role*'s access to *key*. Returns True if the key was present."""
    data = _load_access(project, base_dir)
    keys = data.get(role, [])
    if key not in keys:
        return False
    keys.remove(key)
    data[role] = keys
    _save_access(project, data, base_dir)
    return True


def get_accessible_keys(project: str, role: str, base_dir: Optional[Path] = None) -> List[str]:
    """Return the list of keys *role* is allowed to access in *project*."""
    data = _load_access(project, base_dir)
    return list(data.get(role, []))


def can_access(project: str, role: str, key: str, base_dir: Optional[Path] = None) -> bool:
    """Return True if *role* has access to *key* in *project*."""
    return key in get_accessible_keys(project, role, base_dir)


def list_roles(project: str, base_dir: Optional[Path] = None) -> List[str]:
    """Return all roles that have any access entries for *project*."""
    return list(_load_access(project, base_dir).keys())


def delete_role(project: str, role: str, base_dir: Optional[Path] = None) -> bool:
    """Remove all access entries for *role* in *project*. Returns True if role existed."""
    data = _load_access(project, base_dir)
    if role not in data:
        return False
    del data[role]
    _save_access(project, data, base_dir)
    return True
