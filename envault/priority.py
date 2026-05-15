"""Priority ordering for env keys — assign, retrieve, and sort by priority."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_DEFAULT_PRIORITY = 50
_MIN_PRIORITY = 1
_MAX_PRIORITY = 100


def _priority_path(base_dir: str, project: str) -> Path:
    return Path(base_dir) / f"{project}.priority.json"


def _load_priorities(path: Path) -> Dict[str, int]:
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_priorities(path: Path, data: Dict[str, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_priority(base_dir: str, project: str, key: str, priority: int) -> int:
    """Set the priority for a key (1=highest, 100=lowest). Returns the set value."""
    if not (_MIN_PRIORITY <= priority <= _MAX_PRIORITY):
        raise ValueError(
            f"Priority must be between {_MIN_PRIORITY} and {_MAX_PRIORITY}, got {priority}"
        )
    path = _priority_path(base_dir, project)
    data = _load_priorities(path)
    data[key] = priority
    _save_priorities(path, data)
    return priority


def get_priority(base_dir: str, project: str, key: str) -> int:
    """Return the priority for a key, or the default if not set."""
    path = _priority_path(base_dir, project)
    data = _load_priorities(path)
    return data.get(key, _DEFAULT_PRIORITY)


def remove_priority(base_dir: str, project: str, key: str) -> bool:
    """Remove a key's priority entry. Returns True if it existed."""
    path = _priority_path(base_dir, project)
    data = _load_priorities(path)
    if key not in data:
        return False
    del data[key]
    _save_priorities(path, data)
    return True


def list_priorities(base_dir: str, project: str) -> List[Tuple[str, int]]:
    """Return all (key, priority) pairs sorted by priority ascending (highest first)."""
    path = _priority_path(base_dir, project)
    data = _load_priorities(path)
    return sorted(data.items(), key=lambda x: x[1])


def sort_env_by_priority(
    base_dir: str, project: str, env: Dict[str, str]
) -> List[Tuple[str, str]]:
    """Return env key-value pairs sorted by their assigned priority (ascending)."""
    path = _priority_path(base_dir, project)
    data = _load_priorities(path)
    return sorted(
        env.items(),
        key=lambda kv: data.get(kv[0], _DEFAULT_PRIORITY),
    )
