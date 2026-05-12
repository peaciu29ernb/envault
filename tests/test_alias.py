"""Tests for envault.alias module."""

import pytest
from envault.alias import (
    add_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    resolve_key,
    aliases_for_key,
)


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path / ".envault")


def test_add_alias_and_resolve(base_dir):
    add_alias("db", "DATABASE_URL", base_dir)
    assert resolve_alias("db", base_dir) == "DATABASE_URL"


def test_resolve_alias_missing_returns_none(base_dir):
    assert resolve_alias("nonexistent", base_dir) is None


def test_add_alias_overwrites_existing(base_dir):
    add_alias("db", "DATABASE_URL", base_dir)
    add_alias("db", "POSTGRES_URL", base_dir)
    assert resolve_alias("db", base_dir) == "POSTGRES_URL"


def test_remove_alias_returns_true(base_dir):
    add_alias("token", "API_TOKEN", base_dir)
    result = remove_alias("token", base_dir)
    assert result is True
    assert resolve_alias("token", base_dir) is None


def test_remove_alias_missing_returns_false(base_dir):
    assert remove_alias("ghost", base_dir) is False


def test_list_aliases_empty(base_dir):
    assert list_aliases(base_dir) == {}


def test_list_aliases_multiple(base_dir):
    add_alias("db", "DATABASE_URL", base_dir)
    add_alias("secret", "SECRET_KEY", base_dir)
    result = list_aliases(base_dir)
    assert result == {"db": "DATABASE_URL", "secret": "SECRET_KEY"}


def test_resolve_key_with_alias(base_dir):
    add_alias("pw", "DB_PASSWORD", base_dir)
    assert resolve_key("pw", base_dir) == "DB_PASSWORD"


def test_resolve_key_without_alias_returns_name(base_dir):
    assert resolve_key("MY_KEY", base_dir) == "MY_KEY"


def test_aliases_for_key_single(base_dir):
    add_alias("db", "DATABASE_URL", base_dir)
    add_alias("database", "DATABASE_URL", base_dir)
    result = aliases_for_key("DATABASE_URL", base_dir)
    assert sorted(result) == ["database", "db"]


def test_aliases_for_key_none(base_dir):
    add_alias("db", "DATABASE_URL", base_dir)
    assert aliases_for_key("SECRET_KEY", base_dir) == []


def test_add_alias_raises_on_empty_alias(base_dir):
    with pytest.raises(ValueError):
        add_alias("", "SOME_KEY", base_dir)


def test_add_alias_raises_on_empty_key(base_dir):
    with pytest.raises(ValueError):
        add_alias("myalias", "", base_dir)
