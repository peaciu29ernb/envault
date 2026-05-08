"""Audit log for envault vault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

_DEFAULT_AUDIT_LOG = Path.home() / ".envault" / "audit.log"


def _default_audit_path() -> Path:
    return _DEFAULT_AUDIT_LOG


def _ensure_log_dir(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)


def record_event(
    action: str,
    project: str,
    details: Optional[str] = None,
    log_path: Optional[Path] = None,
) -> dict:
    """Append an audit event to the log file and return the event dict."""
    if log_path is None:
        log_path = _default_audit_path()
    _ensure_log_dir(log_path)

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "project": project,
        "details": details or "",
    }

    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")

    return event


def read_events(
    project: Optional[str] = None,
    log_path: Optional[Path] = None,
) -> List[dict]:
    """Read audit events, optionally filtered by project."""
    if log_path is None:
        log_path = _default_audit_path()

    if not log_path.exists():
        return []

    events = []
    with open(log_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                if project is None or event.get("project") == project:
                    events.append(event)
            except json.JSONDecodeError:
                continue

    return events


def clear_events(log_path: Optional[Path] = None) -> int:
    """Clear all audit events. Returns number of events removed."""
    if log_path is None:
        log_path = _default_audit_path()

    if not log_path.exists():
        return 0

    events = read_events(log_path=log_path)
    count = len(events)
    log_path.write_text("", encoding="utf-8")
    return count
