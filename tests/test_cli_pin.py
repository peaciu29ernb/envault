"""Tests for envault.cli_pin CLI commands."""

from __future__ import annotations

import pytest
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch
from envault.cli_pin import pin_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def pin_dir(tmp_path: Path) -> Path:
    return tmp_path / "pins"


def _patch(pin_dir: Path):
    """Return a context manager that patches the base_dir in cli_pin functions."""
    import envault.pin as pin_mod
    return patch.object(pin_mod, "_DEFAULT_PIN_DIR", pin_dir)


def test_pin_add_success(runner, pin_dir):
    with _patch(pin_dir):
        result = runner.invoke(pin_cmd, ["add", "myproject", "SECRET"])
    assert result.exit_code == 0
    assert "Pinned 'SECRET'" in result.output


def test_pin_add_shows_list(runner, pin_dir):
    with _patch(pin_dir):
        runner.invoke(pin_cmd, ["add", "myproject", "KEY_A"])
        result = runner.invoke(pin_cmd, ["add", "myproject", "KEY_B"])
    assert "KEY_A" in result.output
    assert "KEY_B" in result.output


def test_pin_list_empty(runner, pin_dir):
    with _patch(pin_dir):
        result = runner.invoke(pin_cmd, ["list", "emptyproject"])
    assert result.exit_code == 0
    assert "No pinned keys" in result.output


def test_pin_list_shows_keys(runner, pin_dir):
    with _patch(pin_dir):
        runner.invoke(pin_cmd, ["add", "myproject", "DB_PASS"])
        result = runner.invoke(pin_cmd, ["list", "myproject"])
    assert "DB_PASS" in result.output


def test_pin_remove_success(runner, pin_dir):
    with _patch(pin_dir):
        runner.invoke(pin_cmd, ["add", "myproject", "TOKEN"])
        result = runner.invoke(pin_cmd, ["remove", "myproject", "TOKEN"])
    assert result.exit_code == 0
    assert "Unpinned" in result.output


def test_pin_remove_not_pinned_exits_nonzero(runner, pin_dir):
    with _patch(pin_dir):
        result = runner.invoke(pin_cmd, ["remove", "myproject", "GHOST"])
    assert result.exit_code != 0


def test_pin_check_pinned(runner, pin_dir):
    with _patch(pin_dir):
        runner.invoke(pin_cmd, ["add", "myproject", "API_KEY"])
        result = runner.invoke(pin_cmd, ["check", "myproject", "API_KEY"])
    assert result.exit_code == 0
    assert "is pinned" in result.output


def test_pin_check_not_pinned_exits_nonzero(runner, pin_dir):
    with _patch(pin_dir):
        result = runner.invoke(pin_cmd, ["check", "myproject", "MISSING"])
    assert result.exit_code != 0


def test_pin_clear(runner, pin_dir):
    with _patch(pin_dir):
        runner.invoke(pin_cmd, ["add", "myproject", "X"])
        runner.invoke(pin_cmd, ["add", "myproject", "Y"])
        result = runner.invoke(pin_cmd, ["clear", "myproject"])
    assert result.exit_code == 0
    assert "2" in result.output
