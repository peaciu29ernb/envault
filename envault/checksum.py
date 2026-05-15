"""Checksum utilities for detecting env file tampering or drift."""

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional


def _checksum_path(base_dir: str, project: str) -> Path:
    return Path(base_dir) / f"{project}.checksum.json"


def compute_checksum(env: Dict[str, str]) -> str:
    """Compute a stable SHA-256 checksum over a sorted env dict."""
    stable = json.dumps(env, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(stable.encode()).hexdigest()


def save_checksum(project: str, env: Dict[str, str], base_dir: str = ".envault") -> str:
    """Compute and persist the checksum for a project's env dict."""
    path = _checksum_path(base_dir, project)
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = compute_checksum(env)
    path.write_text(json.dumps({"project": project, "sha256": digest}), encoding="utf-8")
    return digest


def load_checksum(project: str, base_dir: str = ".envault") -> Optional[str]:
    """Load the stored checksum for a project, or None if not found."""
    path = _checksum_path(base_dir, project)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data.get("sha256")


def verify_checksum(project: str, env: Dict[str, str], base_dir: str = ".envault") -> bool:
    """Return True if the env dict matches the stored checksum."""
    stored = load_checksum(project, base_dir)
    if stored is None:
        return False
    return stored == compute_checksum(env)


def delete_checksum(project: str, base_dir: str = ".envault") -> bool:
    """Delete the stored checksum file. Returns True if it existed."""
    path = _checksum_path(base_dir, project)
    if path.exists():
        path.unlink()
        return True
    return False
