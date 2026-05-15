"""Notification hooks for envault events (e.g. key rotation, vault init)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

_HOOKS: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}


def _notify_path(base_dir: Optional[str] = None) -> Path:
    base = Path(base_dir) if base_dir else Path.home() / ".envault"
    return base / "notify_config.json"


def _load_config(base_dir: Optional[str] = None) -> Dict[str, Any]:
    path = _notify_path(base_dir)
    if not path.exists():
        return {"channels": []}
    with path.open() as f:
        return json.load(f)


def _save_config(config: Dict[str, Any], base_dir: Optional[str] = None) -> None:
    path = _notify_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(config, f, indent=2)


def register_hook(event: str, fn: Callable[[Dict[str, Any]], None]) -> None:
    """Register an in-process callback for a named event."""
    _HOOKS.setdefault(event, []).append(fn)


def unregister_hooks(event: str) -> None:
    """Remove all in-process callbacks for a named event."""
    _HOOKS.pop(event, None)


def fire(event: str, payload: Dict[str, Any]) -> List[str]:
    """Invoke all registered hooks for *event* and return list of outcomes."""
    outcomes: List[str] = []
    for fn in _HOOKS.get(event, []):
        try:
            fn(payload)
            outcomes.append("ok")
        except Exception as exc:  # noqa: BLE001
            outcomes.append(f"error: {exc}")
    return outcomes


def add_channel(channel: str, base_dir: Optional[str] = None) -> None:
    """Persist a notification channel name (e.g. 'slack', 'email')."""
    config = _load_config(base_dir)
    if channel not in config["channels"]:
        config["channels"].append(channel)
    _save_config(config, base_dir)


def remove_channel(channel: str, base_dir: Optional[str] = None) -> bool:
    """Remove a persisted channel. Returns True if it existed."""
    config = _load_config(base_dir)
    if channel in config["channels"]:
        config["channels"].remove(channel)
        _save_config(config, base_dir)
        return True
    return False


def list_channels(base_dir: Optional[str] = None) -> List[str]:
    """Return all persisted channel names."""
    return _load_config(base_dir)["channels"]
