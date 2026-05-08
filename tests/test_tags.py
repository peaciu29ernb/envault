"""
tests/test_tags.py — Tests for envault.tags module.
"""

import pytest
from envault.tags import (
    add_tag,
    remove_tag,
    get_tags,
    keys_with_tag,
    all_tags,
    clear_tags,
)


@pytest.fixture
def empty_registry():
    return {}


def test_add_tag_creates_entry(empty_registry):
    reg = add_tag(empty_registry, "myapp", "DB_PASSWORD", "secret")
    assert "secret" in reg["myapp"]["DB_PASSWORD"]


def test_add_tag_no_duplicates(empty_registry):
    reg = add_tag(empty_registry, "myapp", "API_KEY", "secret")
    reg = add_tag(reg, "myapp", "API_KEY", "secret")
    assert reg["myapp"]["API_KEY"].count("secret") == 1


def test_add_multiple_tags(empty_registry):
    reg = add_tag(empty_registry, "myapp", "API_KEY", "secret")
    reg = add_tag(reg, "myapp", "API_KEY", "optional")
    assert set(reg["myapp"]["API_KEY"]) == {"secret", "optional"}


def test_remove_tag_returns_true(empty_registry):
    reg = add_tag(empty_registry, "myapp", "DB_URL", "infra")
    result = remove_tag(reg, "myapp", "DB_URL", "infra")
    assert result is True
    assert "infra" not in reg["myapp"]["DB_URL"]


def test_remove_tag_missing_returns_false(empty_registry):
    result = remove_tag(empty_registry, "myapp", "MISSING_KEY", "secret")
    assert result is False


def test_remove_tag_not_present_returns_false(empty_registry):
    reg = add_tag(empty_registry, "myapp", "KEY", "infra")
    result = remove_tag(reg, "myapp", "KEY", "secret")
    assert result is False


def test_get_tags_returns_list(empty_registry):
    reg = add_tag(empty_registry, "myapp", "SECRET_KEY", "secret")
    tags = get_tags(reg, "myapp", "SECRET_KEY")
    assert isinstance(tags, list)
    assert "secret" in tags


def test_get_tags_missing_key_returns_empty(empty_registry):
    tags = get_tags(empty_registry, "myapp", "NONEXISTENT")
    assert tags == []


def test_keys_with_tag(empty_registry):
    reg = add_tag(empty_registry, "myapp", "DB_PASSWORD", "secret")
    reg = add_tag(reg, "myapp", "API_KEY", "secret")
    reg = add_tag(reg, "myapp", "PORT", "infra")
    keys = keys_with_tag(reg, "myapp", "secret")
    assert set(keys) == {"DB_PASSWORD", "API_KEY"}


def test_keys_with_tag_no_match(empty_registry):
    reg = add_tag(empty_registry, "myapp", "PORT", "infra")
    keys = keys_with_tag(reg, "myapp", "secret")
    assert keys == []


def test_all_tags_returns_full_map(empty_registry):
    reg = add_tag(empty_registry, "myapp", "KEY1", "secret")
    reg = add_tag(reg, "myapp", "KEY2", "infra")
    result = all_tags(reg, "myapp")
    assert "KEY1" in result
    assert "KEY2" in result


def test_all_tags_unknown_project_returns_empty(empty_registry):
    result = all_tags(empty_registry, "unknown")
    assert result == {}


def test_clear_tags_removes_all(empty_registry):
    reg = add_tag(empty_registry, "myapp", "KEY", "secret")
    reg = add_tag(reg, "myapp", "KEY", "infra")
    reg = clear_tags(reg, "myapp", "KEY")
    assert get_tags(reg, "myapp", "KEY") == []


def test_clear_tags_noop_on_missing(empty_registry):
    reg = clear_tags(empty_registry, "myapp", "NONEXISTENT")
    assert reg == {}
