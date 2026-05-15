"""Per-project key quota management for envault."""

import json
from pathlib import Path
from typing import Dict, Optional

DEFAULT_QUOTA = 100


def _quota_path(base_dir: Optional[str] = None) -> Path:
    root = Path(base_dir) if base_dir else Path.home() / ".envault"
    return root / "quotas.json"


def _load_quotas(base_dir: Optional[str] = None) -> Dict[str, int]:
    path = _quota_path(base_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_quotas(quotas: Dict[str, int], base_dir: Optional[str] = None) -> None:
    path = _quota_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(quotas, f, indent=2)


def set_quota(project: str, limit: int, base_dir: Optional[str] = None) -> int:
    """Set the maximum number of keys allowed for a project."""
    if limit < 1:
        raise ValueError("Quota limit must be at least 1.")
    quotas = _load_quotas(base_dir)
    quotas[project] = limit
    _save_quotas(quotas, base_dir)
    return limit


def get_quota(project: str, base_dir: Optional[str] = None) -> int:
    """Return the quota for a project, or the default if not set."""
    quotas = _load_quotas(base_dir)
    return quotas.get(project, DEFAULT_QUOTA)


def remove_quota(project: str, base_dir: Optional[str] = None) -> bool:
    """Remove a custom quota for a project. Returns True if removed."""
    quotas = _load_quotas(base_dir)
    if project not in quotas:
        return False
    del quotas[project]
    _save_quotas(quotas, base_dir)
    return True


def check_quota(project: str, current_count: int, base_dir: Optional[str] = None) -> bool:
    """Return True if current_count is within the project's quota."""
    limit = get_quota(project, base_dir)
    return current_count <= limit


def list_quotas(base_dir: Optional[str] = None) -> Dict[str, int]:
    """Return all explicitly set project quotas."""
    return dict(_load_quotas(base_dir))
