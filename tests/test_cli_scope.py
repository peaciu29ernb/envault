"""Tests for envault.cli_scope CLI commands."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_scope import scope_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path / "scopes")


def _invoke(runner, base_dir, *args):
    return runner.invoke(scope_cmd, [*args, "--base-dir", base_dir])


def test_scope_add_success(runner, base_dir):
    result = _invoke(runner, base_dir, "add", "myapp", "dev", "DB_URL")
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "dev" in result.output


def test_scope_add_no_duplicates(runner, base_dir):
    _invoke(runner, base_dir, "add", "myapp", "dev", "KEY")
    result = _invoke(runner, base_dir, "add", "myapp", "dev", "KEY")
    assert result.exit_code == 0
    assert result.output.count("KEY") >= 1


def test_scope_remove_success(runner, base_dir):
    _invoke(runner, base_dir, "add", "myapp", "dev", "SECRET")
    result = _invoke(runner, base_dir, "remove", "myapp", "dev", "SECRET")
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_scope_remove_missing_key(runner, base_dir):
    result = _invoke(runner, base_dir, "remove", "myapp", "dev", "GHOST")
    assert result.exit_code == 0
    assert "not found" in result.output


def test_scope_list_empty(runner, base_dir):
    result = _invoke(runner, base_dir, "list", "myapp")
    assert result.exit_code == 0
    assert "No scopes" in result.output


def test_scope_list_shows_scopes(runner, base_dir):
    _invoke(runner, base_dir, "add", "myapp", "prod", "API_KEY")
    _invoke(runner, base_dir, "add", "myapp", "dev", "DB")
    result = _invoke(runner, base_dir, "list", "myapp")
    assert "prod" in result.output
    assert "dev" in result.output


def test_scope_show_keys(runner, base_dir):
    _invoke(runner, base_dir, "add", "myapp", "ci", "CI_TOKEN")
    result = _invoke(runner, base_dir, "show", "myapp", "ci")
    assert "CI_TOKEN" in result.output


def test_scope_show_empty(runner, base_dir):
    result = _invoke(runner, base_dir, "show", "myapp", "nonexistent")
    assert "empty or does not exist" in result.output


def test_scope_which_found(runner, base_dir):
    _invoke(runner, base_dir, "add", "myapp", "dev", "SHARED")
    _invoke(runner, base_dir, "add", "myapp", "prod", "SHARED")
    result = _invoke(runner, base_dir, "which", "myapp", "SHARED")
    assert "dev" in result.output
    assert "prod" in result.output


def test_scope_which_not_found(runner, base_dir):
    result = _invoke(runner, base_dir, "which", "myapp", "NOWHERE")
    assert "not in any scope" in result.output
