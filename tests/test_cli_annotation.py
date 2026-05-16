"""Tests for envault.cli_annotation CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_annotation import annotation_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def _invoke(runner, base_dir, *args):
    return runner.invoke(annotation_cmd, [*args, "--base-dir", base_dir])


def test_annotation_set_and_get(runner, base_dir):
    result = _invoke(runner, base_dir, "set", "DB_HOST", "Primary host")
    assert result.exit_code == 0
    assert "Annotated 'DB_HOST'" in result.output

    result = _invoke(runner, base_dir, "get", "DB_HOST")
    assert result.exit_code == 0
    assert "Primary host" in result.output


def test_annotation_get_missing_key(runner, base_dir):
    result = _invoke(runner, base_dir, "get", "MISSING")
    assert result.exit_code == 0
    assert "No annotation" in result.output


def test_annotation_remove_existing(runner, base_dir):
    _invoke(runner, base_dir, "set", "API_KEY", "my key note")
    result = _invoke(runner, base_dir, "remove", "API_KEY")
    assert result.exit_code == 0
    assert "Removed" in result.output

    result = _invoke(runner, base_dir, "get", "API_KEY")
    assert "No annotation" in result.output


def test_annotation_remove_missing(runner, base_dir):
    result = _invoke(runner, base_dir, "remove", "GHOST")
    assert result.exit_code == 0
    assert "No annotation found" in result.output


def test_annotation_list_empty(runner, base_dir):
    result = _invoke(runner, base_dir, "list")
    assert result.exit_code == 0
    assert "No annotations" in result.output


def test_annotation_list_shows_all(runner, base_dir):
    _invoke(runner, base_dir, "set", "A", "note-a")
    _invoke(runner, base_dir, "set", "B", "note-b")
    result = _invoke(runner, base_dir, "list")
    assert result.exit_code == 0
    assert "A: note-a" in result.output
    assert "B: note-b" in result.output


def test_annotation_project_isolation(runner, base_dir):
    _invoke(runner, base_dir, "set", "KEY", "alpha", "--project", "alpha")
    _invoke(runner, base_dir, "set", "KEY", "beta", "--project", "beta")
    r1 = _invoke(runner, base_dir, "get", "KEY", "--project", "alpha")
    r2 = _invoke(runner, base_dir, "get", "KEY", "--project", "beta")
    assert "alpha" in r1.output
    assert "beta" in r2.output
