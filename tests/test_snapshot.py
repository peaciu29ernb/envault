"""Tests for envault.snapshot and cli_snapshot."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.snapshot import (
    save_snapshot,
    load_snapshot,
    list_snapshots,
    delete_snapshot,
)
from envault.cli_snapshot import snapshot_cmd


@pytest.fixture
def snap_dir(tmp_path):
    return tmp_path / "snapshots"


def test_save_snapshot_creates_file(snap_dir):
    record = save_snapshot("myapp", {"FOO": "bar"}, name="v1", base_dir=snap_dir)
    assert record["name"] == "v1"
    assert record["project"] == "myapp"
    assert record["env"] == {"FOO": "bar"}
    assert (snap_dir / "myapp" / "v1.json").exists()


def test_save_snapshot_auto_name(snap_dir):
    record = save_snapshot("myapp", {}, base_dir=snap_dir)
    assert record["name"] is not None
    assert len(list_snapshots("myapp", base_dir=snap_dir)) == 1


def test_load_snapshot_roundtrip(snap_dir):
    save_snapshot("proj", {"KEY": "val"}, name="snap1", base_dir=snap_dir)
    loaded = load_snapshot("proj", "snap1", base_dir=snap_dir)
    assert loaded["env"] == {"KEY": "val"}


def test_load_snapshot_missing_raises(snap_dir):
    with pytest.raises(FileNotFoundError, match="not found"):
        load_snapshot("proj", "ghost", base_dir=snap_dir)


def test_list_snapshots_empty(snap_dir):
    assert list_snapshots("noproject", base_dir=snap_dir) == []


def test_list_snapshots_sorted(snap_dir):
    for name in ["c", "a", "b"]:
        save_snapshot("app", {}, name=name, base_dir=snap_dir)
    assert list_snapshots("app", base_dir=snap_dir) == ["a", "b", "c"]


def test_delete_snapshot(snap_dir):
    save_snapshot("app", {}, name="del_me", base_dir=snap_dir)
    assert delete_snapshot("app", "del_me", base_dir=snap_dir) is True
    assert list_snapshots("app", base_dir=snap_dir) == []


def test_delete_missing_returns_false(snap_dir):
    assert delete_snapshot("app", "nope", base_dir=snap_dir) is False


# --- CLI tests ---

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_list_no_snapshots(runner, tmp_path, monkeypatch):
    monkeypatch.setattr("envault.snapshot.DEFAULT_SNAPSHOT_DIR", tmp_path)
    result = runner.invoke(snapshot_cmd, ["list", "myapp"])
    assert result.exit_code == 0
    assert "No snapshots" in result.output


def test_cli_delete_missing(runner, tmp_path, monkeypatch):
    monkeypatch.setattr("envault.snapshot.DEFAULT_SNAPSHOT_DIR", tmp_path)
    result = runner.invoke(snapshot_cmd, ["delete", "myapp", "ghost"])
    assert result.exit_code != 0
    assert "not found" in result.output
