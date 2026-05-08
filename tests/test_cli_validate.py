"""Tests for envault.cli_validate CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_validate import validate_cmd
from envault.vault import create_vault, save_vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_and_schema(tmp_path):
    """Create a vault file + schema and return (vault_path, schema_path, key_hex)."""
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abcdefghijklmnop"}
    vault_path = tmp_path / ".env.vault"
    vault, key = create_vault(env)
    save_vault(vault, str(vault_path))

    schema = {
        "DATABASE_URL": {"required": True},
        "SECRET_KEY": {"required": True, "pattern": "[A-Za-z0-9]{16,}"},
    }
    schema_path = tmp_path / ".env.schema.json"
    schema_path.write_text(json.dumps(schema))

    return vault_path, schema_path, key.hex()


def test_validate_passes(runner, vault_and_schema):
    vault_path, schema_path, key_hex = vault_and_schema
    result = runner.invoke(
        validate_cmd,
        ["run", str(vault_path), "--schema", str(schema_path), "--key", key_hex],
    )
    assert result.exit_code == 0
    assert "passed" in result.output


def test_validate_fails_missing_key(runner, tmp_path):
    env = {"SECRET_KEY": "abcdefghijklmnop"}  # DATABASE_URL missing
    vault_path = tmp_path / ".env.vault"
    vault, key = create_vault(env)
    save_vault(vault, str(vault_path))

    schema = {"DATABASE_URL": {"required": True}, "SECRET_KEY": {"required": True}}
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(json.dumps(schema))

    result = runner.invoke(
        validate_cmd,
        ["run", str(vault_path), "--schema", str(schema_path), "--key", key.hex()],
    )
    assert result.exit_code == 1
    assert "DATABASE_URL" in result.output


def test_validate_json_output(runner, vault_and_schema):
    vault_path, schema_path, key_hex = vault_and_schema
    result = runner.invoke(
        validate_cmd,
        ["run", str(vault_path), "--schema", str(schema_path),
         "--key", key_hex, "--output", "json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["issues"] == []


def test_validate_missing_schema(runner, vault_and_schema):
    vault_path, _, key_hex = vault_and_schema
    result = runner.invoke(
        validate_cmd,
        ["run", str(vault_path), "--schema", "/nonexistent/schema.json", "--key", key_hex],
    )
    assert result.exit_code == 1


def test_validate_bad_vault(runner, tmp_path):
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(json.dumps({}))
    result = runner.invoke(
        validate_cmd,
        ["run", str(tmp_path / "missing.vault"), "--schema", str(schema_path), "--key", "aabb"],
    )
    assert result.exit_code == 1
