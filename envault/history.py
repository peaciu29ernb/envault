"""Track and retrieve the history of vault operations per project."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

_DEFAULT_HISTORY_DIR = Path.home() / ".envault" / "history"


def _history_path(project: str, base_dir: Optional[Path] = None) -> Path:
    base = base_dir or _DEFAULT_HISTORY_DIR
    return base / f"{project}.jsonl"


def record_history(
    project: str,
    action: str,
    details: Optional[dict] = None,
    base_dir: Optional[Path] = None,
) -> dict:
    """Append a history entry for a project action."""
    path = _history_path(project, base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "project": project,
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details or {},
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def read_history(
    project: str,
    limit: Optional[int] = None,
    action_filter: Optional[str] = None,
    base_dir: Optional[Path] = None,
) -> List[dict]:
    """Read history entries for a project, newest first."""
    path = _history_path(project, base_dir)
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    entries = [json.loads(l) for l in lines]
    if action_filter:
        entries = [e for e in entries if e.get("action") == action_filter]

    entries.reverse()
    if limit is not None:
        entries = entries[:limit]
    return entries


def clear_history(project: str, base_dir: Optional[Path] = None) -> bool:
    """Delete the history file for a project. Returns True if deleted."""
    path = _history_path(project, base_dir)
    if path.exists():
        path.unlink()
        return True
    return False


def list_projects_with_history(base_dir: Optional[Path] = None) -> List[str]:
    """Return project names that have history records."""
    base = base_dir or _DEFAULT_HISTORY_DIR
    if not base.exists():
        return []
    return [p.stem for p in sorted(base.glob("*.jsonl"))]
