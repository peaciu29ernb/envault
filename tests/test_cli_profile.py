"""Tests for envault.cli_profile CLI commands."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.cli_profile import profile_cmd
from envault.profile import save_profile


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def base_dir(tmp_path):
    return tmp_path / "profiles"


def _patch_base(base_dir):
    """Patch DEFAULT_PROFILES_DIR in profile module."""
    import envault.profile as pm
    return patch.object(pm, "DEFAULT_PROFILES_DIR", base_dir)


def test_profile_list_empty(runner, base_dir):
    with _patch_base(base_dir):
        result = runner.invoke(profile_cmd, ["list", "myapp"])
    assert result.exit_code == 0
    assert "No profiles found" in result.output


def test_profile_list_shows_names(runner, base_dir):
    with _patch_base(base_dir):
        save_profile("myapp", "dev", {"K": "v"}, base_dir=base_dir)
        save_profile("myapp", "prod", {"K": "v"}, base_dir=base_dir)
        result = runner.invoke(profile_cmd, ["list", "myapp"])
    assert "dev" in result.output
    assert "prod" in result.output


def test_profile_load_outputs_kv(runner, base_dir):
    with _patch_base(base_dir):
        save_profile("myapp", "dev", {"FOO": "bar"}, base_dir=base_dir)
        result = runner.invoke(profile_cmd, ["load", "myapp", "dev"])
    assert result.exit_code == 0
    assert "FOO=bar" in result.output


def test_profile_load_missing_errors(runner, base_dir):
    with _patch_base(base_dir):
        result = runner.invoke(profile_cmd, ["load", "myapp", "ghost"])
    assert result.exit_code != 0
    assert "ghost" in result.output


def test_profile_delete_existing(runner, base_dir):
    with _patch_base(base_dir):
        save_profile("myapp", "dev", {}, base_dir=base_dir)
        result = runner.invoke(profile_cmd, ["delete", "myapp", "dev"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_profile_delete_missing(runner, base_dir):
    with _patch_base(base_dir):
        result = runner.invoke(profile_cmd, ["delete", "myapp", "ghost"])
    assert result.exit_code == 0
    assert "not found" in result.output


def test_profile_diff_json(runner, base_dir):
    with _patch_base(base_dir):
        save_profile("myapp", "dev", {"A": "1"}, base_dir=base_dir)
        save_profile("myapp", "prod", {"A": "2"}, base_dir=base_dir)
        result = runner.invoke(profile_cmd, ["diff", "myapp", "dev", "prod", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["A"]["status"] == "changed"


def test_profile_diff_identical(runner, base_dir):
    with _patch_base(base_dir):
        save_profile("myapp", "a", {"X": "1"}, base_dir=base_dir)
        save_profile("myapp", "b", {"X": "1"}, base_dir=base_dir)
        result = runner.invoke(profile_cmd, ["diff", "myapp", "a", "b"])
    assert "identical" in result.output
