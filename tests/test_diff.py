"""Tests for envault.diff and envault.cli_diff."""

import os
import pytest
from click.testing import CliRunner

from envault.diff import diff_envs, format_diff, has_changes
from envault.vault import create_vault, save_vault
from envault.cli_diff import diff_cmd


# ---------------------------------------------------------------------------
# Unit tests for diff_envs / format_diff / has_changes
# ---------------------------------------------------------------------------

def test_diff_added_keys():
    result = diff_envs({}, {"FOO": "bar"})
    assert result["added"] == [("FOO", "bar")]
    assert result["removed"] == []
    assert result["changed"] == []


def test_diff_removed_keys():
    result = diff_envs({"FOO": "bar"}, {})
    assert result["removed"] == [("FOO", "bar")]
    assert result["added"] == []


def test_diff_changed_keys():
    result = diff_envs({"FOO": "old"}, {"FOO": "new"})
    assert result["changed"] == [("FOO", "old", "new")]
    assert result["unchanged"] == []


def test_diff_unchanged_keys():
    result = diff_envs({"FOO": "same"}, {"FOO": "same"})
    assert result["unchanged"] == [("FOO", "same")]
    assert result["changed"] == []


def test_has_changes_true():
    diff = diff_envs({"A": "1"}, {"B": "2"})
    assert has_changes(diff) is True


def test_has_changes_false():
    diff = diff_envs({"A": "1"}, {"A": "1"})
    assert has_changes(diff) is False


def test_format_diff_contains_symbols():
    diff = diff_envs({"OLD": "x"}, {"NEW": "y"})
    output = format_diff(diff)
    assert "+ NEW" in output
    assert "- OLD" in output


def test_format_diff_show_values():
    diff = diff_envs({"K": "v1"}, {"K": "v2"})
    output = format_diff(diff, show_values=True)
    assert "v1" in output
    assert "v2" in output


def test_format_diff_hide_values_by_default():
    diff = diff_envs({"K": "secret"}, {"K": "other"})
    output = format_diff(diff, show_values=False)
    assert "secret" not in output


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def two_vaults(tmp_path):
    """Create two vault files with overlapping keys."""
    env_a = {"SHARED": "same", "ONLY_A": "val_a", "CHANGED": "old"}
    env_b = {"SHARED": "same", "ONLY_B": "val_b", "CHANGED": "new"}

    vault_a = str(tmp_path / "a.vault")
    vault_b = str(tmp_path / "b.vault")

    data_a, key_a = create_vault(env_a)
    data_b, key_b = create_vault(env_b)
    save_vault(vault_a, data_a)
    save_vault(vault_b, data_b)

    return vault_a, key_a.hex(), vault_b, key_b.hex()


def test_cli_diff_reports_changes(two_vaults):
    runner = CliRunner()
    vault_a, hex_a, vault_b, hex_b = two_vaults
    result = runner.invoke(diff_cmd, ["run", vault_a, vault_b, "--key-a", hex_a, "--key-b", hex_b])
    assert result.exit_code == 0
    assert "+" in result.output or "-" in result.output or "~" in result.output


def test_cli_diff_no_changes(tmp_path):
    runner = CliRunner()
    env = {"FOO": "bar"}
    data, key = create_vault(env)
    vault = str(tmp_path / "same.vault")
    save_vault(vault, data)
    hex_key = key.hex()
    result = runner.invoke(diff_cmd, ["run", vault, vault, "--key-a", hex_key, "--key-b", hex_key])
    assert result.exit_code == 0
    assert "No differences" in result.output


def test_cli_diff_missing_key_option(two_vaults):
    runner = CliRunner()
    vault_a, _, vault_b, _ = two_vaults
    result = runner.invoke(diff_cmd, ["run", vault_a, vault_b])
    assert result.exit_code != 0
