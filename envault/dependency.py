"""Track dependencies between env keys (e.g. KEY_B depends on KEY_A)."""

import json
from pathlib import Path
from typing import Dict, List, Optional


def _dep_path(base_dir: str, project: str) -> Path:
    return Path(base_dir) / f"{project}.deps.json"


def _load_deps(path: Path) -> Dict[str, List[str]]:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save_deps(path: Path, data: Dict[str, List[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def add_dependency(base_dir: str, project: str, key: str, depends_on: str) -> None:
    """Record that `key` depends on `depends_on`."""
    path = _dep_path(base_dir, project)
    data = _load_deps(path)
    deps = data.setdefault(key, [])
    if depends_on not in deps:
        deps.append(depends_on)
    _save_deps(path, data)


def remove_dependency(base_dir: str, project: str, key: str, depends_on: str) -> bool:
    """Remove a dependency. Returns True if it existed."""
    path = _dep_path(base_dir, project)
    data = _load_deps(path)
    deps = data.get(key, [])
    if depends_on in deps:
        deps.remove(depends_on)
        if not deps:
            del data[key]
        _save_deps(path, data)
        return True
    return False


def get_dependencies(base_dir: str, project: str, key: str) -> List[str]:
    """Return list of keys that `key` depends on."""
    path = _dep_path(base_dir, project)
    data = _load_deps(path)
    return list(data.get(key, []))


def get_dependents(base_dir: str, project: str, key: str) -> List[str]:
    """Return list of keys that depend on `key`."""
    path = _dep_path(base_dir, project)
    data = _load_deps(path)
    return [k for k, deps in data.items() if key in deps]


def all_dependencies(base_dir: str, project: str) -> Dict[str, List[str]]:
    """Return the full dependency map for a project."""
    path = _dep_path(base_dir, project)
    return _load_deps(path)


def check_missing(base_dir: str, project: str, env: Dict[str, str]) -> Dict[str, List[str]]:
    """Return keys whose declared dependencies are absent from env."""
    path = _dep_path(base_dir, project)
    data = _load_deps(path)
    missing: Dict[str, List[str]] = {}
    for key, deps in data.items():
        absent = [d for d in deps if d not in env]
        if absent:
            missing[key] = absent
    return missing
