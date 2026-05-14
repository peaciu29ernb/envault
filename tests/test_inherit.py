"""Tests for envault.inherit and envault.cli_inherit."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.inherit import (
    get_parents,
    remove_parent,
    resolve_env,
    set_parent,
)
from envault.cli_inherit import inherit_cmd


# ---------------------------------------------------------------------------
# Unit tests for inherit.py
# ---------------------------------------------------------------------------


def test_set_parent_adds_entry(tmp_path):
    base = str(tmp_path)
    set_parent("child", "base", base_dir=base)
    assert get_parents("child", base_dir=base) == ["base"]


def test_set_parent_no_duplicates(tmp_path):
    base = str(tmp_path)
    set_parent("child", "base", base_dir=base)
    set_parent("child", "base", base_dir=base)
    assert get_parents("child", base_dir=base) == ["base"]


def test_set_multiple_parents_ordered(tmp_path):
    base = str(tmp_path)
    set_parent("child", "base", base_dir=base)
    set_parent("child", "common", base_dir=base)
    assert get_parents("child", base_dir=base) == ["base", "common"]


def test_remove_parent_returns_true(tmp_path):
    base = str(tmp_path)
    set_parent("child", "base", base_dir=base)
    result = remove_parent("child", "base", base_dir=base)
    assert result is True
    assert get_parents("child", base_dir=base) == []


def test_remove_parent_missing_returns_false(tmp_path):
    base = str(tmp_path)
    result = remove_parent("child", "ghost", base_dir=base)
    assert result is False


def test_get_parents_empty_when_none(tmp_path):
    base = str(tmp_path)
    assert get_parents("unknown", base_dir=base) == []


def test_resolve_env_override_true():
    child = {"A": "child_a", "B": "child_b"}
    parent = {"A": "parent_a", "C": "parent_c"}
    result = resolve_env(child, [parent], override=True)
    assert result["A"] == "child_a"   # child wins
    assert result["B"] == "child_b"
    assert result["C"] == "parent_c"  # inherited


def test_resolve_env_override_false():
    child = {"A": "child_a", "B": "child_b"}
    parent = {"A": "parent_a", "C": "parent_c"}
    result = resolve_env(child, [parent], override=False)
    assert result["A"] == "parent_a"  # parent wins
    assert result["C"] == "parent_c"


def test_resolve_env_multiple_parents_last_wins():
    child: dict = {}
    p1 = {"X": "from_p1"}
    p2 = {"X": "from_p2"}
    result = resolve_env(child, [p1, p2], override=True)
    assert result["X"] == "from_p2"


# ---------------------------------------------------------------------------
# CLI tests for cli_inherit.py
# ---------------------------------------------------------------------------


@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_inherit_add(runner, tmp_path):
    result = runner.invoke(
        inherit_cmd, ["add", "child", "base", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "inherits from 'base'" in result.output


def test_cli_inherit_list(runner, tmp_path):
    base = str(tmp_path)
    set_parent("child", "base", base_dir=base)
    result = runner.invoke(inherit_cmd, ["list", "child", "--base-dir", base])
    assert result.exit_code == 0
    assert "base" in result.output


def test_cli_inherit_list_empty(runner, tmp_path):
    result = runner.invoke(
        inherit_cmd, ["list", "nobody", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "No inheritance" in result.output


def test_cli_inherit_remove_success(runner, tmp_path):
    base = str(tmp_path)
    set_parent("child", "base", base_dir=base)
    result = runner.invoke(inherit_cmd, ["remove", "child", "base", "--base-dir", base])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_cli_inherit_remove_missing(runner, tmp_path):
    result = runner.invoke(
        inherit_cmd, ["remove", "child", "ghost", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code != 0
