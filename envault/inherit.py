"""Inheritance support: merge a base environment into a project env."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import load_vault, save_vault


InheritMap = Dict[str, List[str]]


def _inherit_path(base_dir: str = ".envault") -> Path:
    return Path(base_dir) / "inherit.json"


def _load_inherit(base_dir: str = ".envault") -> InheritMap:
    import json
    path = _inherit_path(base_dir)
    if not path.exists():
        return {}
    with path.open("r") as fh:
        return json.load(fh)


def _save_inherit(data: InheritMap, base_dir: str = ".envault") -> None:
    import json
    path = _inherit_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def set_parent(project: str, parent: str, base_dir: str = ".envault") -> None:
    """Register *parent* as an inheritance source for *project*."""
    data = _load_inherit(base_dir)
    parents: List[str] = data.get(project, [])
    if parent not in parents:
        parents.append(parent)
    data[project] = parents
    _save_inherit(data, base_dir)


def remove_parent(project: str, parent: str, base_dir: str = ".envault") -> bool:
    """Remove *parent* from *project*'s inheritance chain."""
    data = _load_inherit(base_dir)
    parents = data.get(project, [])
    if parent not in parents:
        return False
    parents.remove(parent)
    data[project] = parents
    _save_inherit(data, base_dir)
    return True


def get_parents(project: str, base_dir: str = ".envault") -> List[str]:
    """Return ordered list of parent project names for *project*."""
    return _load_inherit(base_dir).get(project, [])


def resolve_env(
    project_env: Dict[str, str],
    parent_envs: List[Dict[str, str]],
    override: bool = True,
) -> Dict[str, str]:
    """Merge parent envs into *project_env*.

    If *override* is True (default) the child's own keys take precedence.
    Otherwise parent values overwrite child values.
    """
    merged: Dict[str, str] = {}
    for parent in parent_envs:
        merged.update(parent)
    if override:
        merged.update(project_env)
    else:
        project_env.update(merged)
        merged = project_env
    return merged
