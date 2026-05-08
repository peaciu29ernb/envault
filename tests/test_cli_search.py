"""Tests for envault.cli_search."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from envault.cli_search import search_cmd

SAMPLE_ENV = {
    "DATABASE_URL": "postgres://localhost/db",
    "DB_PASS": "secret",
    "APP_KEY": "abc123",
    "DEBUG": "true",
}


@pytest.fixture()
def runner():
    return CliRunner()


def _patch_load(env=SAMPLE_ENV):
    return patch("envault.cli_search.load_vault", return_value=env)


def test_search_keys_glob(runner):
    with _patch_load():
        result = runner.invoke(search_cmd, ["keys", "DB_*"])
    assert result.exit_code == 0
    assert "DB_PASS" in result.output
    assert "DATABASE_URL" not in result.output


def test_search_keys_no_match(runner):
    with _patch_load():
        result = runner.invoke(search_cmd, ["keys", "NOPE_*"])
    assert result.exit_code == 0
    assert "No matching keys found." in result.output


def test_search_keys_regex(runner):
    with _patch_load():
        result = runner.invoke(search_cmd, ["keys", "^DB", "--regex"])
    assert result.exit_code == 0
    assert "DB_PASS" in result.output


def test_search_values_found(runner):
    with _patch_load():
        result = runner.invoke(search_cmd, ["values", "secret"])
    assert result.exit_code == 0
    assert "DB_PASS" in result.output


def test_search_values_not_found(runner):
    with _patch_load():
        result = runner.invoke(search_cmd, ["values", "MISSING"])
    assert result.exit_code == 0
    assert "No matching values found." in result.output


def test_search_prefix(runner):
    with _patch_load():
        result = runner.invoke(search_cmd, ["prefix", "APP"])
    assert result.exit_code == 0
    assert "APP_KEY" in result.output


def test_search_prefix_no_match(runner):
    with _patch_load():
        result = runner.invoke(search_cmd, ["prefix", "ZZZ"])
    assert result.exit_code == 0
    assert "No keys with prefix" in result.output
