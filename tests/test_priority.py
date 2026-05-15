"""Tests for envault.priority module."""

import pytest
from envault.priority import (
    set_priority,
    get_priority,
    remove_priority,
    list_priorities,
    sort_env_by_priority,
    _DEFAULT_PRIORITY,
)


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def test_set_priority_returns_value(base_dir):
    result = set_priority(base_dir, "myapp", "DB_URL", 10)
    assert result == 10


def test_get_priority_returns_set_value(base_dir):
    set_priority(base_dir, "myapp", "API_KEY", 5)
    assert get_priority(base_dir, "myapp", "API_KEY") == 5


def test_get_priority_returns_default_when_not_set(base_dir):
    assert get_priority(base_dir, "myapp", "UNSET_KEY") == _DEFAULT_PRIORITY


def test_set_priority_overwrites_existing(base_dir):
    set_priority(base_dir, "myapp", "DB_URL", 20)
    set_priority(base_dir, "myapp", "DB_URL", 80)
    assert get_priority(base_dir, "myapp", "DB_URL") == 80


def test_set_priority_invalid_too_low_raises(base_dir):
    with pytest.raises(ValueError, match="Priority must be between"):
        set_priority(base_dir, "myapp", "KEY", 0)


def test_set_priority_invalid_too_high_raises(base_dir):
    with pytest.raises(ValueError, match="Priority must be between"):
        set_priority(base_dir, "myapp", "KEY", 101)


def test_set_priority_boundary_values(base_dir):
    assert set_priority(base_dir, "myapp", "A", 1) == 1
    assert set_priority(base_dir, "myapp", "B", 100) == 100


def test_remove_priority_returns_true(base_dir):
    set_priority(base_dir, "myapp", "DB_URL", 10)
    assert remove_priority(base_dir, "myapp", "DB_URL") is True


def test_remove_priority_missing_returns_false(base_dir):
    assert remove_priority(base_dir, "myapp", "GHOST") is False


def test_remove_priority_then_get_returns_default(base_dir):
    set_priority(base_dir, "myapp", "KEY", 15)
    remove_priority(base_dir, "myapp", "KEY")
    assert get_priority(base_dir, "myapp", "KEY") == _DEFAULT_PRIORITY


def test_list_priorities_sorted_ascending(base_dir):
    set_priority(base_dir, "myapp", "C", 90)
    set_priority(base_dir, "myapp", "A", 10)
    set_priority(base_dir, "myapp", "B", 50)
    result = list_priorities(base_dir, "myapp")
    priorities = [p for _, p in result]
    assert priorities == sorted(priorities)


def test_list_priorities_empty_when_none(base_dir):
    assert list_priorities(base_dir, "empty_project") == []


def test_sort_env_by_priority_orders_correctly(base_dir):
    set_priority(base_dir, "myapp", "LOW", 90)
    set_priority(base_dir, "myapp", "HIGH", 5)
    env = {"LOW": "val1", "HIGH": "val2", "MID": "val3"}
    result = sort_env_by_priority(base_dir, "myapp", env)
    keys = [k for k, _ in result]
    assert keys.index("HIGH") < keys.index("MID") < keys.index("LOW")


def test_sort_env_by_priority_unset_keys_use_default(base_dir):
    set_priority(base_dir, "myapp", "FIRST", 1)
    env = {"FIRST": "a", "SECOND": "b"}
    result = sort_env_by_priority(base_dir, "myapp", env)
    assert result[0][0] == "FIRST"
