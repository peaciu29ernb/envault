"""Tests for envault.cli_pipeline."""

import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.cli_pipeline import pipeline_cmd


@pytest.fixture()
def runner():
    return CliRunner()


FAKE_ENV = {"GREETING": "hello", "NAME": "world"}
FAKE_KEY = b"\x00" * 32
FAKE_KEY_HEX = FAKE_KEY.hex()


def _patch_load(env=None):
    return patch("envault.cli_pipeline.load_vault", return_value=env or FAKE_ENV)


def test_pipeline_run_env_output(runner):
    with _patch_load():
        result = runner.invoke(
            pipeline_cmd,
            ["run", "vault.env", "--key", FAKE_KEY_HEX, "--output", "env"],
        )
    assert result.exit_code == 0
    assert "GREETING=hello" in result.output
    assert "NAME=world" in result.output


def test_pipeline_run_json_output(runner):
    with _patch_load():
        result = runner.invoke(
            pipeline_cmd,
            ["run", "vault.env", "--key", FAKE_KEY_HEX, "--output", "json"],
        )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["GREETING"] == "hello"


def test_pipeline_run_with_upper_step(runner):
    with _patch_load():
        result = runner.invoke(
            pipeline_cmd,
            ["run", "vault.env", "--key", FAKE_KEY_HEX,
             "--step", "upcase:upper", "--output", "env"],
        )
    assert result.exit_code == 0
    assert "GREETING=HELLO" in result.output
    assert "NAME=WORLD" in result.output


def test_pipeline_run_invalid_key(runner):
    result = runner.invoke(
        pipeline_cmd,
        ["run", "vault.env", "--key", "notahex"],
    )
    assert result.exit_code != 0
    assert "hex" in result.output.lower()


def test_pipeline_run_invalid_step_format(runner):
    with _patch_load():
        result = runner.invoke(
            pipeline_cmd,
            ["run", "vault.env", "--key", FAKE_KEY_HEX, "--step", "badformat"],
        )
    assert result.exit_code != 0


def test_pipeline_run_vault_load_failure(runner):
    with patch("envault.cli_pipeline.load_vault", side_effect=RuntimeError("bad vault")):
        result = runner.invoke(
            pipeline_cmd,
            ["run", "vault.env", "--key", FAKE_KEY_HEX],
        )
    assert result.exit_code != 0
    assert "bad vault" in result.output


def test_pipeline_list_steps_empty(runner):
    result = runner.invoke(pipeline_cmd, ["list-steps"])
    assert result.exit_code == 0
    assert "No steps" in result.output


def test_pipeline_list_steps_shows_names(runner):
    result = runner.invoke(
        pipeline_cmd,
        ["list-steps", "--step", "upcase:upper", "--step", "bang:append"],
    )
    assert result.exit_code == 0
    assert "upcase" in result.output
    assert "bang" in result.output
