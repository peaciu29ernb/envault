"""Snapshot support: save and compare named snapshots of decrypted vault contents."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_SNAPSHOT_DIR = Path.home() / ".envault" / "snapshots"


def _snapshot_path(project: str, name: str, base_dir: Path = DEFAULT_SNAPSHOT_DIR) -> Path:
    return base_dir / project / f"{name}.json"


def save_snapshot(
    project: str,
    env: dict,
    name: Optional[str] = None,
    base_dir: Path = DEFAULT_SNAPSHOT_DIR,
) -> dict:
    """Persist a named snapshot of env vars for a project."""
    if name is None:
        name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = _snapshot_path(project, name, base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "project": project,
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "env": env,
    }
    path.write_text(json.dumps(record, indent=2))
    return record


def load_snapshot(
    project: str,
    name: str,
    base_dir: Path = DEFAULT_SNAPSHOT_DIR,
) -> dict:
    """Load a previously saved snapshot. Raises FileNotFoundError if missing."""
    path = _snapshot_path(project, name, base_dir)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found for project '{project}'")
    return json.loads(path.read_text())


def list_snapshots(
    project: str,
    base_dir: Path = DEFAULT_SNAPSHOT_DIR,
) -> list:
    """Return sorted list of snapshot names for a project."""
    project_dir = base_dir / project
    if not project_dir.exists():
        return []
    return sorted(
        p.stem for p in project_dir.glob("*.json")
    )


def delete_snapshot(
    project: str,
    name: str,
    base_dir: Path = DEFAULT_SNAPSHOT_DIR,
) -> bool:
    """Delete a snapshot. Returns True if deleted, False if not found."""
    path = _snapshot_path(project, name, base_dir)
    if not path.exists():
        return False
    path.unlink()
    return True
