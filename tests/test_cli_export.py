"""Tests for envault/cli_export.py"""

import json
import pytest
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envault.cli_export import export_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def fake_env():
    return {"APP_ENV": "production", "PORT": "8080"}


def _invoke_export(runner, vault_path, fmt="env", extra_args=None):
    args = ["run", str(vault_path), "--format", fmt]
    if extra_args:
        args.extend(extra_args)
    return runner.invoke(export_cmd, args)


def test_export_env_format(runner, fake_env, tmp_path):
    vault = tmp_path / "test.vault"
    vault.write_bytes(b"dummy")
    with patch("envault.cli_export.retrieve_key", return_value=b"k" * 32), \
         patch("envault.cli_export.load_vault", return_value=fake_env), \
         patch("envault.cli_export.record_event"):
        result = _invoke_export(runner, vault, fmt="env")
    assert result.exit_code == 0
    assert "APP_ENV=production" in result.output
    assert "PORT=8080" in result.output


def test_export_json_format(runner, fake_env, tmp_path):
    vault = tmp_path / "test.vault"
    vault.write_bytes(b"dummy")
    with patch("envault.cli_export.retrieve_key", return_value=b"k" * 32), \
         patch("envault.cli_export.load_vault", return_value=fake_env), \
         patch("envault.cli_export.record_event"):
        result = _invoke_export(runner, vault, fmt="json")
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed == fake_env


def test_export_shell_format(runner, fake_env, tmp_path):
    vault = tmp_path / "test.vault"
    vault.write_bytes(b"dummy")
    with patch("envault.cli_export.retrieve_key", return_value=b"k" * 32), \
         patch("envault.cli_export.load_vault", return_value=fake_env), \
         patch("envault.cli_export.record_event"):
        result = _invoke_export(runner, vault, fmt="shell")
    assert result.exit_code == 0
    assert "export APP_ENV=" in result.output


def test_export_to_file(runner, fake_env, tmp_path):
    vault = tmp_path / "test.vault"
    vault.write_bytes(b"dummy")
    out_file = tmp_path / "out.env"
    with patch("envault.cli_export.retrieve_key", return_value=b"k" * 32), \
         patch("envault.cli_export.load_vault", return_value=fake_env), \
         patch("envault.cli_export.record_event"):
        result = _invoke_export(runner, vault, fmt="env", extra_args=["--output", str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()
    content = out_file.read_text()
    assert "APP_ENV=production" in content


def test_export_missing_vault(runner, tmp_path):
    vault = tmp_path / "missing.vault"
    with patch("envault.cli_export.retrieve_key", return_value=b"k" * 32), \
         patch("envault.cli_export.load_vault", side_effect=FileNotFoundError("not found")):
        result = _invoke_export(runner, vault)
    assert result.exit_code != 0
    assert "Error" in result.output


def test_export_with_password(runner, fake_env, tmp_path):
    vault = tmp_path / "test.vault"
    vault.write_bytes(b"dummy")
    with patch("envault.cli_export.load_vault", return_value=fake_env) as mock_load, \
         patch("envault.cli_export.record_event"):
        result = _invoke_export(runner, vault, extra_args=["--password", "secret"])
    assert result.exit_code == 0
    mock_load.assert_called_once_with(str(vault), password="secret")
