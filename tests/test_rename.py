"""Tests for envault.rename module."""

import pytest
from envault.rename import rename_key, rename_bulk, rename_by_prefix, RenameError


SAMPLE = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_SECRET": "s3cr3t"}


# ---------------------------------------------------------------------------
# rename_key
# ---------------------------------------------------------------------------

def test_rename_key_basic():
    result = rename_key(SAMPLE, "DB_HOST", "DATABASE_HOST")
    assert "DATABASE_HOST" in result
    assert "DB_HOST" not in result
    assert result["DATABASE_HOST"] == "localhost"


def test_rename_key_preserves_other_keys():
    result = rename_key(SAMPLE, "DB_HOST", "DATABASE_HOST")
    assert result["DB_PORT"] == "5432"
    assert result["APP_SECRET"] == "s3cr3t"


def test_rename_key_does_not_mutate_original():
    original = dict(SAMPLE)
    rename_key(original, "DB_HOST", "DATABASE_HOST")
    assert "DB_HOST" in original


def test_rename_key_same_name_returns_copy():
    result = rename_key(SAMPLE, "DB_HOST", "DB_HOST")
    assert result == SAMPLE
    assert result is not SAMPLE


def test_rename_key_missing_raises():
    with pytest.raises(RenameError, match="not found"):
        rename_key(SAMPLE, "MISSING_KEY", "NEW_KEY")


def test_rename_key_collision_raises():
    with pytest.raises(RenameError, match="already exists"):
        rename_key(SAMPLE, "DB_HOST", "DB_PORT")


def test_rename_key_collision_with_overwrite():
    result = rename_key(SAMPLE, "DB_HOST", "DB_PORT", overwrite=True)
    assert result["DB_PORT"] == "localhost"
    assert "DB_HOST" not in result
    # Original DB_PORT value is gone
    assert len(result) == len(SAMPLE) - 1


# ---------------------------------------------------------------------------
# rename_bulk
# ---------------------------------------------------------------------------

def test_rename_bulk_applies_all():
    mapping = {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}
    result = rename_bulk(SAMPLE, mapping)
    assert "DATABASE_HOST" in result
    assert "DATABASE_PORT" in result
    assert "DB_HOST" not in result
    assert "DB_PORT" not in result


def test_rename_bulk_empty_mapping_returns_copy():
    result = rename_bulk(SAMPLE, {})
    assert result == SAMPLE
    assert result is not SAMPLE


def test_rename_bulk_partial_failure_raises():
    mapping = {"DB_HOST": "DATABASE_HOST", "NONEXISTENT": "X"}
    with pytest.raises(RenameError):
        rename_bulk(SAMPLE, mapping)


# ---------------------------------------------------------------------------
# rename_by_prefix
# ---------------------------------------------------------------------------

def test_rename_by_prefix_renames_matching_keys():
    result = rename_by_prefix(SAMPLE, "DB_", "DATABASE_")
    assert "DATABASE_HOST" in result
    assert "DATABASE_PORT" in result
    assert "DB_HOST" not in result
    assert "DB_PORT" not in result


def test_rename_by_prefix_leaves_non_matching_keys():
    result = rename_by_prefix(SAMPLE, "DB_", "DATABASE_")
    assert result["APP_SECRET"] == "s3cr3t"


def test_rename_by_prefix_no_match_raises():
    with pytest.raises(RenameError, match="No keys found"):
        rename_by_prefix(SAMPLE, "MISSING_", "NEW_")


def test_rename_by_prefix_preserves_values():
    result = rename_by_prefix(SAMPLE, "DB_", "DATABASE_")
    assert result["DATABASE_HOST"] == "localhost"
    assert result["DATABASE_PORT"] == "5432"
