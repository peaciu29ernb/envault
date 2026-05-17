"""Tests for envault.cli_typecheck."""
from __future__ import annotations

import json
import os

import pytest
from click.testing import CliRunner

from envault.cli_typecheck import typecheck_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_and_schema(tmp_path, monkeypatch):
    """Create a fake vault file and a schema file, patching load_vault."""
    env = {"PORT": "8080", "DEBUG": "true", "API_URL": "https://api.example.com"}
    schema = {"PORT": "int", "DEBUG": "bool", "API_URL": "url"}

    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(schema))

    vault_file = tmp_path / "test.env.vault"
    vault_file.write_text("")  # content irrelevant; we patch load_vault

    monkeypatch.setattr(
        "envault.cli_typecheck.load_vault",
        lambda path, project=None, password=None: env,
    )
    return str(vault_file), str(schema_file), env


def test_typecheck_check_passes(runner, vault_and_schema):
    vault_file, schema_file, _ = vault_and_schema
    result = runner.invoke(typecheck_cmd, ["check", vault_file, schema_file])
    assert result.exit_code == 0
    assert "passed" in result.output


def test_typecheck_check_json_output(runner, vault_and_schema):
    vault_file, schema_file, _ = vault_and_schema
    result = runner.invoke(typecheck_cmd, ["check", vault_file, schema_file, "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == []


def test_typecheck_check_violation_reported(runner, tmp_path, monkeypatch):
    env = {"PORT": "not-a-number"}
    schema = {"PORT": "int"}
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(schema))
    vault_file = tmp_path / "v.vault"
    vault_file.write_text("")
    monkeypatch.setattr(
        "envault.cli_typecheck.load_vault",
        lambda path, project=None, password=None: env,
    )
    result = runner.invoke(typecheck_cmd, ["check", str(vault_file), str(schema_file)])
    assert "PORT" in result.output
    assert "int" in result.output


def test_typecheck_check_strict_exits_nonzero(runner, tmp_path, monkeypatch):
    env = {"PORT": "bad"}
    schema = {"PORT": "int"}
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(schema))
    vault_file = tmp_path / "v.vault"
    vault_file.write_text("")
    monkeypatch.setattr(
        "envault.cli_typecheck.load_vault",
        lambda path, project=None, password=None: env,
    )
    result = runner.invoke(typecheck_cmd, ["check", str(vault_file), str(schema_file), "--strict"])
    assert result.exit_code != 0


def test_typecheck_infer_output(runner, tmp_path, monkeypatch):
    env = {"PORT": "3000", "FLAG": "true", "NAME": "myapp"}
    vault_file = tmp_path / "v.vault"
    vault_file.write_text("")
    monkeypatch.setattr(
        "envault.cli_typecheck.load_vault",
        lambda path, project=None, password=None: env,
    )
    result = runner.invoke(typecheck_cmd, ["infer", str(vault_file)])
    assert result.exit_code == 0
    assert "int" in result.output
    assert "bool" in result.output
    assert "str" in result.output
