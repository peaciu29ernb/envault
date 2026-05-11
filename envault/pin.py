"""Pin/unpin specific env keys so they are excluded from key rotation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

_DEFAULT_PIN_DIR = Path.home() / ".envault" / "pins"


def _pin_path(project: str, base_dir: Path = _DEFAULT_PIN_DIR) -> Path:
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / f"{project}.json"


def _load_pins(project: str, base_dir: Path = _DEFAULT_PIN_DIR) -> List[str]:
    path = _pin_path(project, base_dir)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_pins(project: str, pins: List[str], base_dir: Path = _DEFAULT_PIN_DIR) -> None:
    path = _pin_path(project, base_dir)
    path.write_text(json.dumps(sorted(set(pins))))


def pin_key(project: str, key: str, base_dir: Path = _DEFAULT_PIN_DIR) -> List[str]:
    """Pin a key for the given project. Returns updated pin list."""
    pins = _load_pins(project, base_dir)
    if key not in pins:
        pins.append(key)
    _save_pins(project, pins, base_dir)
    return sorted(set(pins))


def unpin_key(project: str, key: str, base_dir: Path = _DEFAULT_PIN_DIR) -> bool:
    """Unpin a key. Returns True if it was pinned, False otherwise."""
    pins = _load_pins(project, base_dir)
    if key not in pins:
        return False
    pins = [p for p in pins if p != key]
    _save_pins(project, pins, base_dir)
    return True


def get_pins(project: str, base_dir: Path = _DEFAULT_PIN_DIR) -> List[str]:
    """Return all pinned keys for the given project."""
    return _load_pins(project, base_dir)


def is_pinned(project: str, key: str, base_dir: Path = _DEFAULT_PIN_DIR) -> bool:
    """Check whether a specific key is pinned."""
    return key in _load_pins(project, base_dir)


def clear_pins(project: str, base_dir: Path = _DEFAULT_PIN_DIR) -> int:
    """Remove all pins for a project. Returns number of pins cleared."""
    pins = _load_pins(project, base_dir)
    count = len(pins)
    _pin_path(project, base_dir).unlink(missing_ok=True)
    return count
