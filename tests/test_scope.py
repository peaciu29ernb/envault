"""Tests for envault.scope module."""
from __future__ import annotations

import pytest

from envault import scope as sc


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path / "scopes")


def test_add_to_scope_creates_entry(base_dir):
    keys = sc.add_to_scope(base_dir, "myapp", "dev", "DATABASE_URL")
    assert "DATABASE_URL" in keys


def test_add_to_scope_no_duplicates(base_dir):
    sc.add_to_scope(base_dir, "myapp", "dev", "KEY")
    keys = sc.add_to_scope(base_dir, "myapp", "dev", "KEY")
    assert keys.count("KEY") == 1


def test_add_multiple_keys_to_scope(base_dir):
    sc.add_to_scope(base_dir, "myapp", "prod", "A")
    sc.add_to_scope(base_dir, "myapp", "prod", "B")
    keys = sc.get_scope_keys(base_dir, "myapp", "prod")
    assert set(keys) == {"A", "B"}


def test_remove_from_scope_returns_true(base_dir):
    sc.add_to_scope(base_dir, "myapp", "dev", "SECRET")
    result = sc.remove_from_scope(base_dir, "myapp", "dev", "SECRET")
    assert result is True
    assert "SECRET" not in sc.get_scope_keys(base_dir, "myapp", "dev")


def test_remove_missing_key_returns_false(base_dir):
    result = sc.remove_from_scope(base_dir, "myapp", "dev", "NONEXISTENT")
    assert result is False


def test_get_scope_keys_empty_when_no_scope(base_dir):
    keys = sc.get_scope_keys(base_dir, "myapp", "ci")
    assert keys == []


def test_list_scopes_empty_when_none(base_dir):
    scopes = sc.list_scopes(base_dir, "myapp")
    assert scopes == []


def test_list_scopes_returns_all(base_dir):
    sc.add_to_scope(base_dir, "myapp", "dev", "A")
    sc.add_to_scope(base_dir, "myapp", "prod", "B")
    sc.add_to_scope(base_dir, "myapp", "ci", "C")
    scopes = sc.list_scopes(base_dir, "myapp")
    assert set(scopes) == {"dev", "prod", "ci"}


def test_key_scopes_returns_matching_scopes(base_dir):
    sc.add_to_scope(base_dir, "myapp", "dev", "SHARED")
    sc.add_to_scope(base_dir, "myapp", "prod", "SHARED")
    sc.add_to_scope(base_dir, "myapp", "ci", "OTHER")
    result = sc.key_scopes(base_dir, "myapp", "SHARED")
    assert set(result) == {"dev", "prod"}


def test_key_scopes_not_in_any(base_dir):
    result = sc.key_scopes(base_dir, "myapp", "GHOST")
    assert result == []


def test_filter_env_by_scope(base_dir):
    sc.add_to_scope(base_dir, "myapp", "dev", "DB")
    sc.add_to_scope(base_dir, "myapp", "dev", "PORT")
    env = {"DB": "postgres://", "PORT": "5432", "SECRET": "hidden"}
    result = sc.filter_env_by_scope(base_dir, "myapp", "dev", env)
    assert result == {"DB": "postgres://", "PORT": "5432"}
    assert "SECRET" not in result


def test_filter_env_by_scope_empty_scope(base_dir):
    env = {"A": "1", "B": "2"}
    result = sc.filter_env_by_scope(base_dir, "myapp", "nonexistent", env)
    assert result == {}
