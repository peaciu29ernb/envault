"""Tests for envault.access and envault.cli_access."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.access import (
    grant_access,
    revoke_access,
    get_accessible_keys,
    can_access,
    list_roles,
    delete_role,
)
from envault.cli_access import access_cmd


@pytest.fixture()
def base_dir(tmp_path: Path) -> Path:
    return tmp_path / "access"


# ── unit tests ────────────────────────────────────────────────────────────────

def test_grant_access_adds_key(base_dir):
    keys = grant_access("proj", "admin", "DB_PASSWORD", base_dir)
    assert "DB_PASSWORD" in keys


def test_grant_access_no_duplicates(base_dir):
    grant_access("proj", "admin", "DB_PASSWORD", base_dir)
    keys = grant_access("proj", "admin", "DB_PASSWORD", base_dir)
    assert keys.count("DB_PASSWORD") == 1


def test_grant_multiple_keys(base_dir):
    grant_access("proj", "admin", "KEY_A", base_dir)
    keys = grant_access("proj", "admin", "KEY_B", base_dir)
    assert "KEY_A" in keys and "KEY_B" in keys


def test_revoke_access_returns_true(base_dir):
    grant_access("proj", "admin", "SECRET", base_dir)
    assert revoke_access("proj", "admin", "SECRET", base_dir) is True
    assert "SECRET" not in get_accessible_keys("proj", "admin", base_dir)


def test_revoke_missing_key_returns_false(base_dir):
    assert revoke_access("proj", "admin", "GHOST", base_dir) is False


def test_can_access_true(base_dir):
    grant_access("proj", "viewer", "API_KEY", base_dir)
    assert can_access("proj", "viewer", "API_KEY", base_dir) is True


def test_can_access_false(base_dir):
    assert can_access("proj", "viewer", "API_KEY", base_dir) is False


def test_list_roles_returns_all(base_dir):
    grant_access("proj", "admin", "K1", base_dir)
    grant_access("proj", "viewer", "K2", base_dir)
    roles = list_roles("proj", base_dir)
    assert "admin" in roles and "viewer" in roles


def test_list_roles_empty_when_none(base_dir):
    assert list_roles("proj", base_dir) == []


def test_delete_role_returns_true(base_dir):
    grant_access("proj", "admin", "K1", base_dir)
    assert delete_role("proj", "admin", base_dir) is True
    assert "admin" not in list_roles("proj", base_dir)


def test_delete_role_missing_returns_false(base_dir):
    assert delete_role("proj", "ghost", base_dir) is False


# ── CLI tests ─────────────────────────────────────────────────────────────────

@pytest.fixture()
def runner():
    return CliRunner()


def _patch(base_dir):
    """Return a context manager that patches the default base dir."""
    import unittest.mock as mock
    return mock.patch("envault.access._DEFAULT_BASE", base_dir)


def test_cli_grant_and_list(runner, base_dir):
    with _patch(base_dir):
        result = runner.invoke(access_cmd, ["grant", "proj", "admin", "DB_PASS"])
        assert result.exit_code == 0
        assert "DB_PASS" in result.output

        result = runner.invoke(access_cmd, ["list", "proj", "admin"])
        assert "DB_PASS" in result.output


def test_cli_check_can_access(runner, base_dir):
    with _patch(base_dir):
        runner.invoke(access_cmd, ["grant", "proj", "admin", "TOKEN"])
        result = runner.invoke(access_cmd, ["check", "proj", "admin", "TOKEN"])
        assert "CAN" in result.output


def test_cli_check_cannot_access(runner, base_dir):
    with _patch(base_dir):
        result = runner.invoke(access_cmd, ["check", "proj", "admin", "TOKEN"])
        assert "CANNOT" in result.output


def test_cli_roles(runner, base_dir):
    with _patch(base_dir):
        runner.invoke(access_cmd, ["grant", "proj", "devops", "K"])
        result = runner.invoke(access_cmd, ["roles", "proj"])
        assert "devops" in result.output


def test_cli_delete_role(runner, base_dir):
    with _patch(base_dir):
        runner.invoke(access_cmd, ["grant", "proj", "admin", "K"])
        result = runner.invoke(access_cmd, ["delete-role", "proj", "admin"])
        assert result.exit_code == 0
        assert "Deleted" in result.output
