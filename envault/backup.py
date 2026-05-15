"""Backup and restore encrypted vault files."""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def _backup_dir(base_dir: Optional[str] = None) -> Path:
    if base_dir:
        return Path(base_dir)
    return Path.home() / ".envault" / "backups"


def _backup_path(project: str, name: str, base_dir: Optional[str] = None) -> Path:
    return _backup_dir(base_dir) / project / f"{name}.env.vault.bak"


def create_backup(
    project: str,
    vault_path: str,
    name: Optional[str] = None,
    base_dir: Optional[str] = None,
) -> str:
    """Copy a vault file to the backup store. Returns the backup file path."""
    if not os.path.exists(vault_path):
        raise FileNotFoundError(f"Vault file not found: {vault_path}")

    if name is None:
        name = datetime.utcnow().strftime("%Y%m%dT%H%M%S")

    dest = _backup_path(project, name, base_dir)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(vault_path, dest)

    meta_path = dest.with_suffix(".json")
    meta = {
        "project": project,
        "name": name,
        "source": str(vault_path),
        "created_at": datetime.utcnow().isoformat(),
    }
    meta_path.write_text(json.dumps(meta, indent=2))
    return str(dest)


def restore_backup(
    project: str,
    name: str,
    dest_path: str,
    base_dir: Optional[str] = None,
) -> str:
    """Restore a named backup to dest_path. Returns dest_path."""
    src = _backup_path(project, name, base_dir)
    if not src.exists():
        raise FileNotFoundError(f"Backup '{name}' not found for project '{project}'")
    shutil.copy2(src, dest_path)
    return dest_path


def list_backups(project: str, base_dir: Optional[str] = None) -> List[dict]:
    """Return metadata dicts for all backups of a project, newest first."""
    project_dir = _backup_dir(base_dir) / project
    if not project_dir.exists():
        return []
    entries = []
    for meta_file in sorted(project_dir.glob("*.json"), reverse=True):
        try:
            entries.append(json.loads(meta_file.read_text()))
        except (json.JSONDecodeError, OSError):
            continue
    return entries


def delete_backup(
    project: str, name: str, base_dir: Optional[str] = None
) -> bool:
    """Delete a named backup. Returns True if deleted, False if not found."""
    bak = _backup_path(project, name, base_dir)
    meta = bak.with_suffix(".json")
    if not bak.exists():
        return False
    bak.unlink(missing_ok=True)
    meta.unlink(missing_ok=True)
    return True
