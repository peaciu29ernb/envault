"""Tests for envault.archive."""

from __future__ import annotations

import os
import pytest

from envault.archive import (
    create_archive,
    delete_archive,
    extract_archive,
    list_archives,
)


@pytest.fixture()
def vault_file(tmp_path):
    """A minimal fake vault file."""
    p = tmp_path / "vault.enc"
    p.write_bytes(b"encrypted-payload-data")
    return str(p)


@pytest.fixture()
def arch_dir(tmp_path):
    return str(tmp_path / "archives")


# ---------------------------------------------------------------------------
# create_archive
# ---------------------------------------------------------------------------

def test_create_archive_returns_path(vault_file, arch_dir):
    path = create_archive("myproject", vault_file, name="v1", base_dir=arch_dir)
    assert path.exists()
    assert path.suffix == ".gz"


def test_create_archive_auto_name(vault_file, arch_dir):
    path = create_archive("myproject", vault_file, base_dir=arch_dir)
    assert path.exists()
    assert "myproject__" in path.name


def test_create_archive_missing_vault_raises(tmp_path, arch_dir):
    with pytest.raises(FileNotFoundError, match="Vault file not found"):
        create_archive("myproject", str(tmp_path / "missing.enc"), base_dir=arch_dir)


def test_create_archive_contains_vault_and_meta(vault_file, arch_dir):
    import tarfile

    path = create_archive("myproject", vault_file, name="check", base_dir=arch_dir)
    with tarfile.open(str(path), "r:gz") as tar:
        names = tar.getnames()
    assert "vault.enc" in names
    assert "meta.json" in names


# ---------------------------------------------------------------------------
# extract_archive
# ---------------------------------------------------------------------------

def test_extract_archive_restores_content(vault_file, arch_dir, tmp_path):
    create_archive("proj", vault_file, name="snap1", base_dir=arch_dir)
    out = str(tmp_path / "restored.enc")
    extract_archive("proj", "snap1", out, base_dir=arch_dir)
    assert open(out, "rb").read() == b"encrypted-payload-data"


def test_extract_archive_missing_raises(arch_dir, tmp_path):
    with pytest.raises(FileNotFoundError, match="Archive not found"):
        extract_archive("proj", "ghost", str(tmp_path / "out.enc"), base_dir=arch_dir)


# ---------------------------------------------------------------------------
# list_archives
# ---------------------------------------------------------------------------

def test_list_archives_empty_when_none(arch_dir):
    assert list_archives("proj", base_dir=arch_dir) == []


def test_list_archives_returns_names(vault_file, arch_dir):
    create_archive("proj", vault_file, name="alpha", base_dir=arch_dir)
    create_archive("proj", vault_file, name="beta", base_dir=arch_dir)
    names = list_archives("proj", base_dir=arch_dir)
    assert "alpha" in names
    assert "beta" in names


def test_list_archives_scoped_to_project(vault_file, arch_dir):
    create_archive("proj_a", vault_file, name="v1", base_dir=arch_dir)
    create_archive("proj_b", vault_file, name="v1", base_dir=arch_dir)
    assert list_archives("proj_a", base_dir=arch_dir) == ["v1"]
    assert list_archives("proj_b", base_dir=arch_dir) == ["v1"]


# ---------------------------------------------------------------------------
# delete_archive
# ---------------------------------------------------------------------------

def test_delete_archive_returns_true(vault_file, arch_dir):
    create_archive("proj", vault_file, name="todel", base_dir=arch_dir)
    assert delete_archive("proj", "todel", base_dir=arch_dir) is True
    assert list_archives("proj", base_dir=arch_dir) == []


def test_delete_archive_missing_returns_false(arch_dir):
    assert delete_archive("proj", "nope", base_dir=arch_dir) is False
