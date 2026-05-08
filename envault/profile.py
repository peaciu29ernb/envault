"""Profile support: manage multiple named env profiles (dev, staging, prod) per project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_PROFILES_DIR = Path(".envault") / "profiles"


def _profile_path(project: str, profile: str, base_dir: Optional[Path] = None) -> Path:
    base = base_dir or DEFAULT_PROFILES_DIR
    return base / project / f"{profile}.json"


def save_profile(project: str, profile: str, data: Dict[str, str], base_dir: Optional[Path] = None) -> Path:
    """Persist a named profile (plain dict) for a project."""
    path = _profile_path(project, profile, base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def load_profile(project: str, profile: str, base_dir: Optional[Path] = None) -> Dict[str, str]:
    """Load a named profile for a project. Raises FileNotFoundError if missing."""
    path = _profile_path(project, profile, base_dir)
    if not path.exists():
        raise FileNotFoundError(f"Profile '{profile}' not found for project '{project}'")
    return json.loads(path.read_text(encoding="utf-8"))


def list_profiles(project: str, base_dir: Optional[Path] = None) -> List[str]:
    """Return sorted list of profile names for a project."""
    base = base_dir or DEFAULT_PROFILES_DIR
    project_dir = base / project
    if not project_dir.exists():
        return []
    return sorted(p.stem for p in project_dir.glob("*.json"))


def delete_profile(project: str, profile: str, base_dir: Optional[Path] = None) -> bool:
    """Delete a profile. Returns True if deleted, False if not found."""
    path = _profile_path(project, profile, base_dir)
    if not path.exists():
        return False
    path.unlink()
    return True


def diff_profiles(project: str, profile_a: str, profile_b: str, base_dir: Optional[Path] = None) -> Dict[str, dict]:
    """Return a summary of differences between two profiles."""
    a = load_profile(project, profile_a, base_dir)
    b = load_profile(project, profile_b, base_dir)
    all_keys = set(a) | set(b)
    result: Dict[str, dict] = {}
    for key in sorted(all_keys):
        if key not in a:
            result[key] = {"status": "added", "value": b[key]}
        elif key not in b:
            result[key] = {"status": "removed", "value": a[key]}
        elif a[key] != b[key]:
            result[key] = {"status": "changed", "from": a[key], "to": b[key]}
    return result
