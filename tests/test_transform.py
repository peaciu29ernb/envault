"""Tests for envault.transform module and CLI."""

import json
import pytest
from click.testing import CliRunner
from envault.transform import (
    apply_transform,
    apply_transforms,
    transform_env,
    list_transforms,
    TransformError,
)
from envault.cli_transform import transform_cmd


# --- Unit tests ---

def test_apply_transform_upper():
    assert apply_transform("hello", "upper") == "HELLO"


def test_apply_transform_lower():
    assert apply_transform("WORLD", "lower") == "world"


def test_apply_transform_strip():
    assert apply_transform("  hi  ", "strip") == "hi"


def test_apply_transform_trim_quotes():
    assert apply_transform("'value'", "trim_quotes") == "value"


def test_apply_transform_base64_roundtrip():
    original = "secret123"
    encoded = apply_transform(original, "base64_encode")
    decoded = apply_transform(encoded, "base64_decode")
    assert decoded == original


def test_apply_transform_url_encode():
    result = apply_transform("hello world", "url_encode")
    assert result == "hello%20world"


def test_apply_transform_unknown_raises():
    with pytest.raises(TransformError, match="Unknown transform"):
        apply_transform("value", "nonexistent")


def test_apply_transforms_pipeline():
    result = apply_transforms("  Hello World  ", ["strip", "upper"])
    assert result == "HELLO WORLD"


def test_apply_transforms_empty_pipeline():
    assert apply_transforms("unchanged", []) == "unchanged"


def test_transform_env_single_key():
    env = {"DB_HOST": "localhost", "API_KEY": "secret"}
    result = transform_env(env, {"DB_HOST": ["upper"]})
    assert result["DB_HOST"] == "LOCALHOST"
    assert result["API_KEY"] == "secret"


def test_transform_env_glob_pattern():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "myapp"}
    result = transform_env(env, {"DB_*": ["upper"]})
    assert result["DB_HOST"] == "LOCALHOST"
    assert result["DB_PORT"] == "5432"
    assert result["APP_NAME"] == "myapp"


def test_transform_env_missing_key_skip():
    env = {"A": "val"}
    result = transform_env(env, {"MISSING": ["upper"]}, skip_missing=True)
    assert result == {"A": "val"}


def test_transform_env_missing_key_raises():
    env = {"A": "val"}
    with pytest.raises(TransformError, match="No keys matched"):
        transform_env(env, {"MISSING": ["upper"]}, skip_missing=False)


def test_list_transforms_returns_list():
    names = list_transforms()
    assert isinstance(names, list)
    assert "upper" in names
    assert "lower" in names
    assert "base64_encode" in names


# --- CLI tests ---

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_list_transforms(runner):
    result = runner.invoke(transform_cmd, ["list"])
    assert result.exit_code == 0
    assert "upper" in result.output
    assert "lower" in result.output


def test_cli_apply_dry_run(runner, tmp_path):
    from envault.vault import create_vault, save_vault
    vault_file = str(tmp_path / "test.vault")
    env, key = create_vault({"GREETING": "hello"})
    save_vault(vault_file, env, key=key)
    result = runner.invoke(
        transform_cmd,
        ["apply", vault_file, "GREETING", "upper", "--dry-run"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "HELLO" in result.output


def test_cli_batch_dry_run(runner, tmp_path):
    from envault.vault import create_vault, save_vault
    vault_file = str(tmp_path / "test.vault")
    rules_file = str(tmp_path / "rules.json")
    env, key = create_vault({"NAME": "  world  ", "TAG": "dev"})
    save_vault(vault_file, env, key=key)
    rules = {"NAME": ["strip", "upper"], "TAG": ["upper"]}
    with open(rules_file, "w") as f:
        json.dump(rules, f)
    result = runner.invoke(
        transform_cmd,
        ["batch", vault_file, rules_file, "--dry-run"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "WORLD" in result.output
