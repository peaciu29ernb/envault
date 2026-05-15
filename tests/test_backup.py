"""Tests for envault.backup module."""

import os
import pytest
from pathlib import Path
from envault.backup import (
    create_backup,
    restore_backup,
    list_backups,
    delete_backup,
)


@pytest.fixture
def tmp_vault(tmp_path):
    vault_file = tmp_path / "test.env.vault"
    vault_file.write_bytes(b"encrypted-content-xyz")
    return str(vault_file)


@pytest.fixture
def backup_base(tmp_path):
    return str(tmp_path / "backups")


def test_create_backup_returns_path(tmp_vault, backup_base):
    path = create_backup("myproject", tmp_vault, name="v1", base_dir=backup_base)
    assert path.endswith(".bak")
    assert os.path.exists(path)


def test_create_backup_copies_content(tmp_vault, backup_base):
    path = create_backup("myproject", tmp_vault, name="v1", base_dir=backup_base)
    assert Path(path).read_bytes() == b"encrypted-content-xyz"


def test_create_backup_writes_metadata(tmp_vault, backup_base):
    path = create_backup("myproject", tmp_vault, name="v1", base_dir=backup_base)
    meta_path = Path(path).with_suffix(".json")
    assert meta_path.exists()
    import json
    meta = json.loads(meta_path.read_text())
    assert meta["project"] == "myproject"
    assert meta["name"] == "v1"


def test_create_backup_auto_name(tmp_vault, backup_base):
    path = create_backup("myproject", tmp_vault, base_dir=backup_base)
    assert os.path.exists(path)


def test_create_backup_missing_vault_raises(tmp_path, backup_base):
    with pytest.raises(FileNotFoundError, match="Vault file not found"):
        create_backup("myproject", str(tmp_path / "nonexistent.vault"), base_dir=backup_base)


def test_list_backups_empty_when_none(backup_base):
    result = list_backups("myproject", base_dir=backup_base)
    assert result == []


def test_list_backups_returns_metadata(tmp_vault, backup_base):
    create_backup("myproject", tmp_vault, name="snap1", base_dir=backup_base)
    create_backup("myproject", tmp_vault, name="snap2", base_dir=backup_base)
    entries = list_backups("myproject", base_dir=backup_base)
    names = [e["name"] for e in entries]
    assert "snap1" in names
    assert "snap2" in names


def test_list_backups_newest_first(tmp_vault, backup_base):
    create_backup("myproject", tmp_vault, name="aaa", base_dir=backup_base)
    create_backup("myproject", tmp_vault, name="zzz", base_dir=backup_base)
    entries = list_backups("myproject", base_dir=backup_base)
    assert entries[0]["name"] == "zzz"


def test_restore_backup_writes_file(tmp_vault, backup_base, tmp_path):
    create_backup("myproject", tmp_vault, name="v1", base_dir=backup_base)
    dest = str(tmp_path / "restored.vault")
    result = restore_backup("myproject", "v1", dest, base_dir=backup_base)
    assert result == dest
    assert Path(dest).read_bytes() == b"encrypted-content-xyz"


def test_restore_backup_missing_raises(backup_base, tmp_path):
    dest = str(tmp_path / "out.vault")
    with pytest.raises(FileNotFoundError, match="Backup 'ghost' not found"):
        restore_backup("myproject", "ghost", dest, base_dir=backup_base)


def test_delete_backup_returns_true(tmp_vault, backup_base):
    create_backup("myproject", tmp_vault, name="v1", base_dir=backup_base)
    assert delete_backup("myproject", "v1", base_dir=backup_base) is True


def test_delete_backup_removes_files(tmp_vault, backup_base):
    path = create_backup("myproject", tmp_vault, name="v1", base_dir=backup_base)
    delete_backup("myproject", "v1", base_dir=backup_base)
    assert not os.path.exists(path)
    assert list_backups("myproject", base_dir=backup_base) == []


def test_delete_backup_missing_returns_false(backup_base):
    assert delete_backup("myproject", "nope", base_dir=backup_base) is False
