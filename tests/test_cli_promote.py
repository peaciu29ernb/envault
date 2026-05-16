"""CLI tests for the promote command."""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from envault.cli_promote import promote_cmd


@pytest.fixture()
def runner():
    return CliRunner()


SOURCE_ENV = {"DB_HOST": "prod", "DB_PORT": "5432", "SECRET": "abc"}
TARGET_ENV = {"DB_HOST": "staging", "APP_ENV": "staging"}
FAKE_KEY = b"k" * 32


def _patch_load(src_env=None, tgt_env=None):
    src_env = src_env or SOURCE_ENV
    tgt_env = tgt_env or TARGET_ENV

    def _load(path):
        if "source" in path:
            return dict(src_env), FAKE_KEY
        return dict(tgt_env), FAKE_KEY

    return patch("envault.cli_promote.load_vault", side_effect=_load)


def test_promote_dry_run_no_write(runner):
    with _patch_load(), \
         patch("envault.cli_promote.save_vault") as mock_save:
        result = runner.invoke(
            promote_cmd, ["run", "source.vault", "target.vault", "--dry-run"]
        )
        assert result.exit_code == 0
        assert "dry-run" in result.output
        mock_save.assert_not_called()


def test_promote_writes_on_success(runner):
    with _patch_load(), \
         patch("envault.cli_promote.save_vault") as mock_save:
        result = runner.invoke(
            promote_cmd, ["run", "source.vault", "target.vault"]
        )
        assert result.exit_code == 0
        mock_save.assert_called_once()


def test_promote_json_output(runner):
    with _patch_load(), \
         patch("envault.cli_promote.save_vault"):
        result = runner.invoke(
            promote_cmd,
            ["run", "source.vault", "target.vault", "--format", "json"],
        )
        assert result.exit_code == 0
        import json
        data = json.loads(result.output.split("\n\n")[0])
        assert isinstance(data, list)
        assert all("key" in item and "action" in item for item in data)


def test_promote_missing_key_shows_error(runner):
    with _patch_load(), \
         patch("envault.cli_promote.save_vault"):
        result = runner.invoke(
            promote_cmd,
            ["run", "source.vault", "target.vault", "-k", "NONEXISTENT"],
        )
        assert result.exit_code != 0
        assert "NONEXISTENT" in result.output


def test_promote_overwrite_flag(runner):
    saved_env = {}

    def _save(path, env, key):
        saved_env.update(env)

    with _patch_load(), patch("envault.cli_promote.save_vault", side_effect=_save):
        result = runner.invoke(
            promote_cmd,
            ["run", "source.vault", "target.vault", "--overwrite"],
        )
        assert result.exit_code == 0
        assert saved_env.get("DB_HOST") == "prod"
