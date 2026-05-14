"""Tests for envault.namespace and envault.cli_namespace."""

import pytest
from click.testing import CliRunner
from envault.namespace import (
    add_to_namespace,
    remove_from_namespace,
    get_namespace_keys,
    list_namespaces,
    resolve_namespace,
    filter_env_by_namespace,
)
from envault.cli_namespace import namespace_cmd


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


# --- Unit tests ---

def test_add_to_namespace_creates_entry(base_dir):
    keys = add_to_namespace("proj", "db", "DB_HOST", base_dir)
    assert "DB_HOST" in keys


def test_add_to_namespace_no_duplicates(base_dir):
    add_to_namespace("proj", "db", "DB_HOST", base_dir)
    keys = add_to_namespace("proj", "db", "DB_HOST", base_dir)
    assert keys.count("DB_HOST") == 1


def test_add_multiple_keys_to_namespace(base_dir):
    add_to_namespace("proj", "db", "DB_HOST", base_dir)
    add_to_namespace("proj", "db", "DB_PORT", base_dir)
    keys = get_namespace_keys("proj", "db", base_dir)
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys


def test_remove_from_namespace_returns_true(base_dir):
    add_to_namespace("proj", "db", "DB_HOST", base_dir)
    result = remove_from_namespace("proj", "db", "DB_HOST", base_dir)
    assert result is True


def test_remove_missing_key_returns_false(base_dir):
    result = remove_from_namespace("proj", "db", "NONEXISTENT", base_dir)
    assert result is False


def test_remove_last_key_deletes_namespace(base_dir):
    add_to_namespace("proj", "db", "DB_HOST", base_dir)
    remove_from_namespace("proj", "db", "DB_HOST", base_dir)
    assert "db" not in list_namespaces("proj", base_dir)


def test_list_namespaces_empty(base_dir):
    assert list_namespaces("proj", base_dir) == []


def test_list_namespaces_multiple(base_dir):
    add_to_namespace("proj", "db", "DB_HOST", base_dir)
    add_to_namespace("proj", "cache", "REDIS_URL", base_dir)
    ns = list_namespaces("proj", base_dir)
    assert "db" in ns
    assert "cache" in ns


def test_resolve_namespace_found(base_dir):
    add_to_namespace("proj", "auth", "JWT_SECRET", base_dir)
    ns = resolve_namespace("proj", "JWT_SECRET", base_dir)
    assert ns == "auth"


def test_resolve_namespace_not_found(base_dir):
    ns = resolve_namespace("proj", "UNKNOWN_KEY", base_dir)
    assert ns is None


def test_filter_env_by_namespace(base_dir):
    add_to_namespace("proj", "db", "DB_HOST", base_dir)
    add_to_namespace("proj", "db", "DB_PORT", base_dir)
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
    filtered = filter_env_by_namespace("proj", "db", env, base_dir)
    assert filtered == {"DB_HOST": "localhost", "DB_PORT": "5432"}
    assert "SECRET" not in filtered


# --- CLI tests ---

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_namespace_add(runner, base_dir):
    result = runner.invoke(namespace_cmd, ["add", "proj", "db", "DB_HOST", "--base-dir", base_dir])
    assert result.exit_code == 0
    assert "Added" in result.output


def test_cli_namespace_list_empty(runner, base_dir):
    result = runner.invoke(namespace_cmd, ["list", "proj", "--base-dir", base_dir])
    assert result.exit_code == 0
    assert "No namespaces" in result.output


def test_cli_namespace_show(runner, base_dir):
    add_to_namespace("proj", "db", "DB_URL", base_dir)
    result = runner.invoke(namespace_cmd, ["show", "proj", "db", "--base-dir", base_dir])
    assert result.exit_code == 0
    assert "DB_URL" in result.output


def test_cli_namespace_resolve(runner, base_dir):
    add_to_namespace("proj", "auth", "API_KEY", base_dir)
    result = runner.invoke(namespace_cmd, ["resolve", "proj", "API_KEY", "--base-dir", base_dir])
    assert result.exit_code == 0
    assert "auth" in result.output
