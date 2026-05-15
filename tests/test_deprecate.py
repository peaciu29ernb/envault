"""Tests for envault.deprecate and envault.cli_deprecate."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.deprecate import (
    mark_deprecated,
    unmark_deprecated,
    is_deprecated,
    get_deprecation_info,
    list_deprecated,
    check_env_deprecations,
)
from envault.cli_deprecate import deprecate_cmd


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path / ".envault")


@pytest.fixture
def runner():
    return CliRunner()


def test_mark_deprecated_creates_entry(base_dir):
    info = mark_deprecated("OLD_KEY", base_dir, reason="replaced", replacement="NEW_KEY")
    assert info["reason"] == "replaced"
    assert info["replacement"] == "NEW_KEY"


def test_is_deprecated_true_after_mark(base_dir):
    mark_deprecated("OLD_KEY", base_dir)
    assert is_deprecated("OLD_KEY", base_dir) is True


def test_is_deprecated_false_when_not_marked(base_dir):
    assert is_deprecated("SOME_KEY", base_dir) is False


def test_unmark_deprecated_returns_true(base_dir):
    mark_deprecated("OLD_KEY", base_dir)
    result = unmark_deprecated("OLD_KEY", base_dir)
    assert result is True
    assert is_deprecated("OLD_KEY", base_dir) is False


def test_unmark_deprecated_missing_returns_false(base_dir):
    assert unmark_deprecated("NONEXISTENT", base_dir) is False


def test_get_deprecation_info_returns_metadata(base_dir):
    mark_deprecated("API_KEY", base_dir, reason="use token", replacement="API_TOKEN")
    info = get_deprecation_info("API_KEY", base_dir)
    assert info is not None
    assert info["reason"] == "use token"
    assert info["replacement"] == "API_TOKEN"


def test_get_deprecation_info_none_for_unknown(base_dir):
    assert get_deprecation_info("UNKNOWN", base_dir) is None


def test_list_deprecated_returns_all(base_dir):
    mark_deprecated("A", base_dir, reason="old")
    mark_deprecated("B", base_dir, replacement="C")
    data = list_deprecated(base_dir)
    assert "A" in data
    assert "B" in data


def test_check_env_deprecations_finds_matches(base_dir):
    mark_deprecated("OLD_DB_URL", base_dir, reason="use DATABASE_URL", replacement="DATABASE_URL")
    env = {"OLD_DB_URL": "postgres://...", "PORT": "5432"}
    warnings = check_env_deprecations(env, base_dir)
    assert len(warnings) == 1
    assert warnings[0]["key"] == "OLD_DB_URL"


def test_check_env_deprecations_empty_when_no_matches(base_dir):
    mark_deprecated("UNUSED", base_dir)
    env = {"PORT": "8080", "HOST": "localhost"}
    assert check_env_deprecations(env, base_dir) == []


def test_cli_add_and_list(runner, tmp_path):
    base = str(tmp_path / ".envault")
    result = runner.invoke(deprecate_cmd, ["add", "LEGACY_KEY", "--reason", "old", "--base-dir", base])
    assert result.exit_code == 0
    assert "LEGACY_KEY" in result.output

    result = runner.invoke(deprecate_cmd, ["list", "--base-dir", base])
    assert result.exit_code == 0
    assert "LEGACY_KEY" in result.output


def test_cli_remove(runner, tmp_path):
    base = str(tmp_path / ".envault")
    runner.invoke(deprecate_cmd, ["add", "OLD", "--base-dir", base])
    result = runner.invoke(deprecate_cmd, ["remove", "OLD", "--base-dir", base])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_cli_check_deprecated(runner, tmp_path):
    base = str(tmp_path / ".envault")
    runner.invoke(deprecate_cmd, ["add", "TOKEN", "--reason", "use JWT", "--base-dir", base])
    result = runner.invoke(deprecate_cmd, ["check", "TOKEN", "--base-dir", base])
    assert result.exit_code == 0
    assert "deprecated" in result.output
    assert "use JWT" in result.output


def test_cli_check_not_deprecated(runner, tmp_path):
    base = str(tmp_path / ".envault")
    result = runner.invoke(deprecate_cmd, ["check", "FRESH_KEY", "--base-dir", base])
    assert result.exit_code == 0
    assert "not deprecated" in result.output
