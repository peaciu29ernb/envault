"""envault.archive — Create and manage compressed archives of vault files."""

from __future__ import annotations

import json
import os
import tarfile
import tempfile
import time
from pathlib import Path
from typing import List, Optional


def _archive_dir(base_dir: Optional[str] = None) -> Path:
    root = Path(base_dir) if base_dir else Path.home() / ".envault" / "archives"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _archive_path(project: str, name: str, base_dir: Optional[str] = None) -> Path:
    return _archive_dir(base_dir) / f"{project}__{name}.tar.gz"


def create_archive(
    project: str,
    vault_path: str,
    name: Optional[str] = None,
    base_dir: Optional[str] = None,
) -> Path:
    """Compress *vault_path* into a named .tar.gz archive for *project*."""
    if not os.path.isfile(vault_path):
        raise FileNotFoundError(f"Vault file not found: {vault_path}")

    label = name or str(int(time.time()))
    dest = _archive_path(project, label, base_dir)

    meta = {
        "project": project,
        "name": label,
        "created_at": time.time(),
        "source": os.path.abspath(vault_path),
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as mf:
        json.dump(meta, mf, indent=2)
        meta_path = mf.name

    try:
        with tarfile.open(dest, "w:gz") as tar:
            tar.add(vault_path, arcname="vault.enc")
            tar.add(meta_path, arcname="meta.json")
    finally:
        os.unlink(meta_path)

    return dest


def extract_archive(
    project: str,
    name: str,
    output_path: str,
    base_dir: Optional[str] = None,
) -> str:
    """Extract the vault file from an archive to *output_path*."""
    src = _archive_path(project, name, base_dir)
    if not src.exists():
        raise FileNotFoundError(f"Archive not found: {src}")

    with tarfile.open(src, "r:gz") as tar:
        member = tar.getmember("vault.enc")
        with tar.extractfile(member) as fh:  # type: ignore[union-attr]
            data = fh.read()

    with open(output_path, "wb") as out:
        out.write(data)

    return output_path


def list_archives(project: str, base_dir: Optional[str] = None) -> List[str]:
    """Return sorted list of archive names for *project*."""
    prefix = f"{project}__"
    names = [
        p.stem.replace(prefix, "", 1).replace(".tar", "")
        for p in _archive_dir(base_dir).glob(f"{prefix}*.tar.gz")
    ]
    return sorted(names)


def delete_archive(
    project: str, name: str, base_dir: Optional[str] = None
) -> bool:
    """Delete a named archive. Returns True if deleted, False if not found."""
    path = _archive_path(project, name, base_dir)
    if path.exists():
        path.unlink()
        return True
    return False
