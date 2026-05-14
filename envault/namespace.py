"""Namespace support for grouping env keys under logical prefixes."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


def _namespace_path(base_dir: str, project: str) -> Path:
    return Path(base_dir) / project / "namespaces.json"


def _load_namespaces(path: Path) -> Dict[str, List[str]]:
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_namespaces(path: Path, data: Dict[str, List[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def add_to_namespace(project: str, namespace: str, key: str, base_dir: str) -> List[str]:
    """Add a key to a namespace. Returns updated key list."""
    path = _namespace_path(base_dir, project)
    data = _load_namespaces(path)
    keys = data.setdefault(namespace, [])
    if key not in keys:
        keys.append(key)
    _save_namespaces(path, data)
    return keys


def remove_from_namespace(project: str, namespace: str, key: str, base_dir: str) -> bool:
    """Remove a key from a namespace. Returns True if removed."""
    path = _namespace_path(base_dir, project)
    data = _load_namespaces(path)
    keys = data.get(namespace, [])
    if key not in keys:
        return False
    keys.remove(key)
    if not keys:
        del data[namespace]
    _save_namespaces(path, data)
    return True


def get_namespace_keys(project: str, namespace: str, base_dir: str) -> List[str]:
    """Return all keys in a namespace."""
    path = _namespace_path(base_dir, project)
    data = _load_namespaces(path)
    return data.get(namespace, [])


def list_namespaces(project: str, base_dir: str) -> List[str]:
    """Return all namespace names for a project."""
    path = _namespace_path(base_dir, project)
    data = _load_namespaces(path)
    return sorted(data.keys())


def resolve_namespace(project: str, key: str, base_dir: str) -> Optional[str]:
    """Return the namespace that contains the given key, or None."""
    path = _namespace_path(base_dir, project)
    data = _load_namespaces(path)
    for ns, keys in data.items():
        if key in keys:
            return ns
    return None


def filter_env_by_namespace(
    project: str, namespace: str, env: Dict[str, str], base_dir: str
) -> Dict[str, str]:
    """Return only env entries whose keys belong to the given namespace."""
    ns_keys = set(get_namespace_keys(project, namespace, base_dir))
    return {k: v for k, v in env.items() if k in ns_keys}
