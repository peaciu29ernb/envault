"""Group related env keys together under named groups."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _group_path(base_dir: str) -> Path:
    return Path(base_dir) / ".envault" / "groups.json"


def _load_groups(base_dir: str) -> Dict[str, List[str]]:
    path = _group_path(base_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_groups(base_dir: str, data: Dict[str, List[str]]) -> None:
    path = _group_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def add_to_group(base_dir: str, group: str, key: str) -> List[str]:
    """Add a key to a named group. Returns the updated key list."""
    data = _load_groups(base_dir)
    keys = data.get(group, [])
    if key not in keys:
        keys.append(key)
    data[group] = keys
    _save_groups(base_dir, data)
    return keys


def remove_from_group(base_dir: str, group: str, key: str) -> bool:
    """Remove a key from a group. Returns True if removed, False if not found."""
    data = _load_groups(base_dir)
    keys = data.get(group, [])
    if key not in keys:
        return False
    keys.remove(key)
    data[group] = keys
    _save_groups(base_dir, data)
    return True


def get_group(base_dir: str, group: str) -> List[str]:
    """Return keys belonging to a group."""
    return _load_groups(base_dir).get(group, [])


def list_groups(base_dir: str) -> List[str]:
    """Return all group names."""
    return list(_load_groups(base_dir).keys())


def delete_group(base_dir: str, group: str) -> bool:
    """Delete an entire group. Returns True if deleted, False if not found."""
    data = _load_groups(base_dir)
    if group not in data:
        return False
    del data[group]
    _save_groups(base_dir, data)
    return True


def key_groups(base_dir: str, key: str) -> List[str]:
    """Return all groups that contain a given key."""
    data = _load_groups(base_dir)
    return [g for g, keys in data.items() if key in keys]
