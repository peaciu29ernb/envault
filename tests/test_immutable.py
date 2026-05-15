"""Tests for envault.immutable."""

import pytest
from pathlib import Path
from envault.immutable import (
    mark_immutable,
    unmark_immutable,
    is_immutable,
    get_immutable_keys,
    assert_mutable,
)


@pytest.fixture
def base_dir(tmp_path: Path) -> Path:
    return tmp_path / "immutable"


def test_mark_immutable_adds_key(base_dir):
    result = mark_immutable("proj", "SECRET_KEY", base_dir)
    assert "SECRET_KEY" in result


def test_mark_immutable_no_duplicates(base_dir):
    mark_immutable("proj", "SECRET_KEY", base_dir)
    result = mark_immutable("proj", "SECRET_KEY", base_dir)
    assert result.count("SECRET_KEY") == 1


def test_mark_multiple_keys(base_dir):
    mark_immutable("proj", "KEY_A", base_dir)
    mark_immutable("proj", "KEY_B", base_dir)
    keys = get_immutable_keys("proj", base_dir)
    assert "KEY_A" in keys
    assert "KEY_B" in keys


def test_get_immutable_keys_empty_when_none(base_dir):
    assert get_immutable_keys("unknown_proj", base_dir) == []


def test_is_immutable_true_after_mark(base_dir):
    mark_immutable("proj", "DB_PASSWORD", base_dir)
    assert is_immutable("proj", "DB_PASSWORD", base_dir) is True


def test_is_immutable_false_when_not_marked(base_dir):
    assert is_immutable("proj", "SOME_KEY", base_dir) is False


def test_unmark_immutable_returns_true(base_dir):
    mark_immutable("proj", "API_KEY", base_dir)
    result = unmark_immutable("proj", "API_KEY", base_dir)
    assert result is True


def test_unmark_immutable_removes_key(base_dir):
    mark_immutable("proj", "API_KEY", base_dir)
    unmark_immutable("proj", "API_KEY", base_dir)
    assert is_immutable("proj", "API_KEY", base_dir) is False


def test_unmark_immutable_missing_returns_false(base_dir):
    result = unmark_immutable("proj", "NONEXISTENT", base_dir)
    assert result is False


def test_keys_are_sorted(base_dir):
    mark_immutable("proj", "ZEBRA", base_dir)
    mark_immutable("proj", "ALPHA", base_dir)
    mark_immutable("proj", "MANGO", base_dir)
    keys = get_immutable_keys("proj", base_dir)
    assert keys == sorted(keys)


def test_assert_mutable_raises_for_immutable_key(base_dir):
    mark_immutable("proj", "LOCKED", base_dir)
    with pytest.raises(ValueError, match="immutable"):
        assert_mutable("proj", "LOCKED", base_dir)


def test_assert_mutable_passes_for_mutable_key(base_dir):
    # Should not raise
    assert_mutable("proj", "FREE_KEY", base_dir)


def test_projects_are_isolated(base_dir):
    mark_immutable("proj_a", "SHARED_KEY", base_dir)
    assert is_immutable("proj_b", "SHARED_KEY", base_dir) is False
