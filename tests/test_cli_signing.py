"""Tests for the signing CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envault.cli_signing import signing_cmd
from envault.signing import attach_signature, SIGNATURE_KEY

SECRET = b"testsecretkey678901234567890abc1"
SAMPLE_ENV = {"HOST": "localhost", "PORT": "5432"}


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def signed_env():
    """Return a SAMPLE_ENV dict with a valid signature attached."""
    return attach_signature(SAMPLE_ENV, SECRET)


def _patch_vault(env):
    return patch("envault.cli_signing.load_vault", return_value=env)


def _patch_key(key):
    return patch("envault.cli_signing.retrieve_key", return_value=key)


def test_sign_verify_valid(runner, signed_env):
    with _patch_vault(signed_env), _patch_key(SECRET):
        result = runner.invoke(signing_cmd, ["verify", "vault.enc", "myproject"])
    assert result.exit_code == 0
    assert "valid" in result.output


def test_sign_verify_invalid_signature(runner, signed_env):
    signed_env["EXTRA"] = "tampered"
    with _patch_vault(signed_env), _patch_key(SECRET):
        result = runner.invoke(signing_cmd, ["verify", "vault.enc", "myproject"])
    assert result.exit_code == 3
    assert "INVALID" in result.output


def test_sign_verify_no_signature_in_vault(runner):
    with _patch_vault(SAMPLE_ENV), _patch_key(SECRET):
        result = runner.invoke(signing_cmd, ["verify", "vault.enc", "myproject"])
    assert result.exit_code == 2
    assert "No signature" in result.output


def test_sign_attach_outputs_signature_key(runner):
    with _patch_vault(SAMPLE_ENV), _patch_key(SECRET):
        result = runner.invoke(signing_cmd, ["attach", "vault.enc", "myproject"])
    assert result.exit_code == 0
    assert SIGNATURE_KEY in result.output


def test_sign_missing_project_key(runner):
    with patch("envault.cli_signing.retrieve_key", side_effect=KeyError("missing")):
        result = runner.invoke(signing_cmd, ["verify", "vault.enc", "ghost"])
    assert result.exit_code == 1
    assert "No key found" in result.output


def test_sign_attach_verify_roundtrip(runner):
    """Attaching a signature and then verifying it should succeed end-to-end."""
    with _patch_vault(SAMPLE_ENV), _patch_key(SECRET):
        attach_result = runner.invoke(signing_cmd, ["attach", "vault.enc", "myproject"])
    assert attach_result.exit_code == 0

    signed_env = attach_signature(SAMPLE_ENV, SECRET)
    with _patch_vault(signed_env), _patch_key(SECRET):
        verify_result = runner.invoke(signing_cmd, ["verify", "vault.enc", "myproject"])
    assert verify_result.exit_code == 0
    assert "valid" in verify_result.output
