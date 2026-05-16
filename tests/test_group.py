"""Tests for envault.group module."""
import pytest
from pathlib import Path
from envault.group import (
    add_to_group,
    remove_from_group,
    get_group,
    list_groups,
    delete_group,
    key_groups,
)


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def test_add_to_group_creates_entry(base_dir):
    keys = add_to_group(base_dir, "database", "DB_HOST")
    assert "DB_HOST" in keys


def test_add_to_group_no_duplicates(base_dir):
    add_to_group(base_dir, "database", "DB_HOST")
    keys = add_to_group(base_dir, "database", "DB_HOST")
    assert keys.count("DB_HOST") == 1


def test_add_multiple_keys_to_group(base_dir):
    add_to_group(base_dir, "database", "DB_HOST")
    add_to_group(base_dir, "database", "DB_PORT")
    keys = get_group(base_dir, "database")
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys


def test_get_group_empty_when_none(base_dir):
    assert get_group(base_dir, "nonexistent") == []


def test_remove_from_group_returns_true(base_dir):
    add_to_group(base_dir, "auth", "SECRET_KEY")
    result = remove_from_group(base_dir, "auth", "SECRET_KEY")
    assert result is True
    assert "SECRET_KEY" not in get_group(base_dir, "auth")


def test_remove_from_group_missing_returns_false(base_dir):
    result = remove_from_group(base_dir, "auth", "MISSING_KEY")
    assert result is False


def test_list_groups_empty_when_none(base_dir):
    assert list_groups(base_dir) == []


def test_list_groups_returns_names(base_dir):
    add_to_group(base_dir, "database", "DB_HOST")
    add_to_group(base_dir, "auth", "SECRET_KEY")
    groups = list_groups(base_dir)
    assert "database" in groups
    assert "auth" in groups


def test_delete_group_returns_true(base_dir):
    add_to_group(base_dir, "temp", "TEMP_KEY")
    result = delete_group(base_dir, "temp")
    assert result is True
    assert "temp" not in list_groups(base_dir)


def test_delete_group_missing_returns_false(base_dir):
    assert delete_group(base_dir, "ghost") is False


def test_key_groups_returns_all_containing_groups(base_dir):
    add_to_group(base_dir, "database", "DB_HOST")
    add_to_group(base_dir, "infra", "DB_HOST")
    add_to_group(base_dir, "auth", "SECRET_KEY")
    groups = key_groups(base_dir, "DB_HOST")
    assert "database" in groups
    assert "infra" in groups
    assert "auth" not in groups


def test_key_groups_missing_key_returns_empty(base_dir):
    add_to_group(base_dir, "database", "DB_HOST")
    assert key_groups(base_dir, "UNKNOWN") == []


def test_groups_persist_across_calls(base_dir):
    add_to_group(base_dir, "cache", "REDIS_URL")
    add_to_group(base_dir, "cache", "REDIS_PORT")
    # Re-read from disk
    keys = get_group(base_dir, "cache")
    assert len(keys) == 2
    assert "REDIS_URL" in keys
    assert "REDIS_PORT" in keys
