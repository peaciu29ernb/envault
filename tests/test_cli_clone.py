"""Tests for envault.cli_clone."""

from __future__ import annotations

import json
import os

import pytest
from click.testing import CliRunner

from envault.cli_clone import clone_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def two_vaults(tmp_path):
    """Create two tiny pre-encrypted vaults and return their paths."""
    from envault.vault import create_vault, save_vault

    src = str(tmp_path / "src.vault")
    dst = str(tmp_path / "dst.vault")

    src_env = {"APP_HOST": "localhost", "APP_PORT": "8080", "DB_PASS": "s3cr3t"}
    dst_env = {"EXISTING": "yes"}

    _, src_key = create_vault(src_env, src)
    _, dst_key = create_vault(dst_env, dst)

    return src, dst, src_key, dst_key


def _patch_load_save(monkeypatch, src_env, src_meta, dst_env, dst_meta, written):
    """Monkeypatch load_vault / save_vault for CLI tests."""
    import envault.cli_clone as mod

    def fake_load(path):
        if "src" in path:
            return src_env, src_meta
        return dst_env, dst_meta

    def fake_save(path, env, key, password=None):
        written.update(env)

    monkeypatch.setattr(mod, "load_vault", fake_load)
    monkeypatch.setattr(mod, "save_vault", fake_save)


def test_clone_run_basic(runner, monkeypatch):
    written = {}
    _patch_load_save(
        monkeypatch,
        src_env={"A": "1", "B": "2"},
        src_meta={"key": b"k"},
        dst_env={},
        dst_meta={"key": b"k"},
        written=written,
    )
    result = runner.invoke(clone_cmd, ["run", "src.vault", "dst.vault"])
    assert result.exit_code == 0
    assert "2 key(s)" in result.output


def test_clone_run_dry_run_does_not_write(runner, monkeypatch):
    written = {}
    _patch_load_save(
        monkeypatch,
        src_env={"X": "10"},
        src_meta={"key": b"k"},
        dst_env={},
        dst_meta={"key": b"k"},
        written=written,
    )
    result = runner.invoke(clone_cmd, ["run", "src.vault", "dst.vault", "--dry-run"])
    assert result.exit_code == 0
    assert written == {}
    assert "X" in result.output


def test_clone_run_skip_existing_without_overwrite(runner, monkeypatch):
    written = {}
    _patch_load_save(
        monkeypatch,
        src_env={"KEY": "new"},
        src_meta={"key": b"k"},
        dst_env={"KEY": "old"},
        dst_meta={"key": b"k"},
        written=written,
    )
    result = runner.invoke(clone_cmd, ["run", "src.vault", "dst.vault"])
    assert result.exit_code == 0
    assert "Skipping" in result.output


def test_clone_run_report_flag(runner, monkeypatch):
    written = {}
    _patch_load_save(
        monkeypatch,
        src_env={"A": "1", "B": "2"},
        src_meta={"key": b"k"},
        dst_env={},
        dst_meta={"key": b"k"},
        written=written,
    )
    result = runner.invoke(clone_cmd, ["run", "src.vault", "dst.vault", "--report"])
    assert result.exit_code == 0
    data = json.loads(result.output.split("Cloned")[0])
    assert data["original_count"] == 2
