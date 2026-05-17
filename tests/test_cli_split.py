"""Tests for envault.cli_split."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.cli_split import split_cmd


FAKE_ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "REDIS_URL": "redis://localhost",
    "APP_DEBUG": "true",
}


@pytest.fixture()
def runner():
    return CliRunner()


def _patch_load(env=None):
    return patch("envault.cli_split.load_vault", return_value=env or FAKE_ENV)


# ---------------------------------------------------------------------------
# split prefix
# ---------------------------------------------------------------------------

def test_split_prefix_basic(runner):
    with _patch_load():
        result = runner.invoke(split_cmd, ["prefix", "vault.env", "DB_", "REDIS_"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["DB_"]["DB_HOST"] == "localhost"
    assert data["REDIS_"]["REDIS_URL"] == "redis://localhost"
    assert "APP_DEBUG" in data["__rest__"]


def test_split_prefix_strip(runner):
    with _patch_load():
        result = runner.invoke(split_cmd, ["prefix", "vault.env", "--strip", "DB_"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "HOST" in data["DB_"]
    assert "PORT" in data["DB_"]


def test_split_prefix_no_rest(runner):
    with _patch_load():
        result = runner.invoke(split_cmd, ["prefix", "vault.env", "--no-rest", "DB_"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "__rest__" not in data


# ---------------------------------------------------------------------------
# split glob
# ---------------------------------------------------------------------------

def test_split_glob_basic(runner):
    with _patch_load():
        result = runner.invoke(
            split_cmd,
            ["glob", "vault.env", "-p", "db=DB_*", "-p", "redis=REDIS_*"],
        )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["db"]["DB_HOST"] == "localhost"
    assert data["redis"]["REDIS_URL"] == "redis://localhost"


def test_split_glob_bad_pattern_format(runner):
    with _patch_load():
        result = runner.invoke(split_cmd, ["glob", "vault.env", "-p", "no-equals"])
    assert result.exit_code != 0
    assert "NAME=VALUE" in result.output


def test_split_glob_no_rest(runner):
    with _patch_load():
        result = runner.invoke(
            split_cmd,
            ["glob", "vault.env", "--no-rest", "-p", "all=*"],
        )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "__rest__" not in data


# ---------------------------------------------------------------------------
# split regex
# ---------------------------------------------------------------------------

def test_split_regex_basic(runner):
    with _patch_load():
        result = runner.invoke(
            split_cmd,
            ["regex", "vault.env", "-p", r"db=^DB_", "-p", r"redis=^REDIS_"],
        )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["db"]["DB_HOST"] == "localhost"


def test_split_regex_invalid_pattern(runner):
    with _patch_load():
        result = runner.invoke(
            split_cmd,
            ["regex", "vault.env", "-p", r"bad=[invalid"],
        )
    assert result.exit_code != 0
    assert "Invalid regex" in result.output
