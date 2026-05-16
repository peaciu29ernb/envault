"""Per-key annotation support: attach human-readable notes to env keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


def _annotation_path(base_dir: str, project: str) -> Path:
    return Path(base_dir) / f"{project}.annotations.json"


def _load_annotations(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_annotations(path: Path, data: Dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def set_annotation(key: str, note: str, project: str = "default", base_dir: str = ".envault") -> str:
    """Attach a note to *key* for the given project.  Returns the note."""
    path = _annotation_path(base_dir, project)
    data = _load_annotations(path)
    data[key] = note
    _save_annotations(path, data)
    return note


def get_annotation(key: str, project: str = "default", base_dir: str = ".envault") -> Optional[str]:
    """Return the note attached to *key*, or None if absent."""
    path = _annotation_path(base_dir, project)
    return _load_annotations(path).get(key)


def remove_annotation(key: str, project: str = "default", base_dir: str = ".envault") -> bool:
    """Remove the annotation for *key*.  Returns True if it existed."""
    path = _annotation_path(base_dir, project)
    data = _load_annotations(path)
    if key not in data:
        return False
    del data[key]
    _save_annotations(path, data)
    return True


def list_annotations(project: str = "default", base_dir: str = ".envault") -> Dict[str, str]:
    """Return all annotations for the project as {key: note}."""
    path = _annotation_path(base_dir, project)
    return _load_annotations(path)


def annotate_env(env: Dict[str, str], project: str = "default", base_dir: str = ".envault") -> Dict[str, Optional[str]]:
    """Return a mapping of every key in *env* to its annotation (or None)."""
    notes = list_annotations(project=project, base_dir=base_dir)
    return {k: notes.get(k) for k in env}
