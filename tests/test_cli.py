"""Tests for the envault CLI."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.cli import cli
from envault.keystore import _default_keystore_path


SAMPLE_ENV = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n"


@pytest.fixture(autouse=True)
def isolated_keystore(tmp_path, monkeypatch):
    """Redirect keystore to a temp file for each test."""
    ks_path = tmp_path / "keystore.json"
    monkeypatch.setattr("envault.keystore._default_keystore_path", lambda: ks_path)
    monkeypatch.setattr("envault.cli.store_key", __import__("envault.keystore", fromlist=["store_key"]).store_key)
    monkeypatch.setattr("envault.cli.retrieve_key", __import__("envault.keystore", fromlist=["retrieve_key"]).retrieve_key)
    monkeypatch.setattr("envault.cli.delete_key", __import__("envault.keystore", fromlist=["delete_key"]).delete_key)
    monkeypatch.setattr("envault.cli.list_projects", __import__("envault.keystore", fromlist=["list_projects"]).list_projects)
    return ks_path


def test_init_creates_vault(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path(".env").write_text(SAMPLE_ENV)
        result = runner.invoke(cli, ["init", "myproject"])
        assert result.exit_code == 0
        assert Path("myproject.vault").exists()
        assert "Vault created" in result.output


def test_init_missing_env_file(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "myproject"])
        assert result.exit_code == 1
        assert "not found" in result.output


def test_init_and_decrypt_roundtrip(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path(".env").write_text(SAMPLE_ENV)
        runner.invoke(cli, ["init", "myproject"])
        result = runner.invoke(cli, ["decrypt", "myproject", "--output", "out.env"])
        assert result.exit_code == 0
        content = Path("out.env").read_text()
        assert "DB_HOST=localhost" in content
        assert "SECRET=abc123" in content


def test_init_with_password_and_decrypt(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path(".env").write_text(SAMPLE_ENV)
        runner.invoke(cli, ["init", "myproject", "--password", "s3cr3t"])
        result = runner.invoke(cli, ["decrypt", "myproject", "--password", "s3cr3t", "--output", "out.env"])
        assert result.exit_code == 0
        assert "DB_PORT=5432" in Path("out.env").read_text()


def test_rotate_key(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path(".env").write_text(SAMPLE_ENV)
        runner.invoke(cli, ["init", "myproject"])
        result = runner.invoke(cli, ["rotate", "myproject"])
        assert result.exit_code == 0
        assert "rotated" in result.output
        # Verify we can still decrypt after rotation
        dec = runner.invoke(cli, ["decrypt", "myproject", "--output", "out.env"])
        assert dec.exit_code == 0


def test_list_projects(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path(".env").write_text(SAMPLE_ENV)
        runner.invoke(cli, ["init", "alpha"])
        runner.invoke(cli, ["init", "beta"])
        result = runner.invoke(cli, ["list"])
        assert "alpha" in result.output
        assert "beta" in result.output


def test_list_empty(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["list"])
        assert "No projects" in result.output


def test_delete_project(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path(".env").write_text(SAMPLE_ENV)
        runner.invoke(cli, ["init", "myproject"])
        result = runner.invoke(cli, ["delete", "myproject"])
        assert "removed" in result.output


def test_delete_nonexistent_project(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["delete", "ghost"])
        assert "No key found" in result.output
