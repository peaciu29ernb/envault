"""Tests for envault.clone."""

from __future__ import annotations

import pytest

from envault.clone import CloneError, clone_env, clone_report


ENV = {
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_HOST": "db.local",
    "DB_PASS": "secret",
    "DEBUG": "true",
}


def test_clone_env_full_copy():
    result = clone_env(ENV)
    assert result == ENV
    assert result is not ENV


def test_clone_env_include_subset():
    result = clone_env(ENV, include=["APP_HOST", "DEBUG"])
    assert result == {"APP_HOST": "localhost", "DEBUG": "true"}


def test_clone_env_include_missing_key_silently_skipped():
    result = clone_env(ENV, include=["APP_HOST", "NONEXISTENT"])
    assert result == {"APP_HOST": "localhost"}


def test_clone_env_exclude_keys():
    result = clone_env(ENV, exclude={"DB_HOST", "DB_PASS"})
    assert "DB_HOST" not in result
    assert "DB_PASS" not in result
    assert "APP_HOST" in result


def test_clone_env_prefix_filter():
    result = clone_env(ENV, prefix="APP_")
    assert set(result.keys()) == {"APP_HOST", "APP_PORT"}


def test_clone_env_prefix_strip():
    result = clone_env(ENV, prefix="APP_", strip_prefix=True)
    assert set(result.keys()) == {"HOST", "PORT"}
    assert result["HOST"] == "localhost"


def test_clone_env_strip_prefix_without_prefix_ignored():
    result = clone_env(ENV, strip_prefix=True)
    assert result == ENV


def test_clone_env_transform_applied():
    result = clone_env(ENV, include=["DEBUG"], transform=lambda k, v: (k, v.upper()))
    assert result["DEBUG"] == "TRUE"


def test_clone_env_transform_rename():
    result = clone_env(
        {"FOO": "bar"},
        transform=lambda k, v: ("NEW_" + k, v),
    )
    assert result == {"NEW_FOO": "bar"}


def test_clone_env_transform_duplicate_key_raises():
    with pytest.raises(CloneError, match="Duplicate key"):
        clone_env(
            {"A": "1", "B": "2"},
            transform=lambda k, v: ("SAME", v),
        )


def test_clone_env_transform_bad_type_raises():
    with pytest.raises(CloneError):
        clone_env({"X": "1"}, transform=lambda k, v: (123, v))  # type: ignore[return-value]


def test_clone_env_empty_source():
    assert clone_env({}) == {}


def test_clone_report_basic():
    cloned = {"HOST": "localhost", "PORT": "8080"}
    original = {"APP_HOST": "localhost", "APP_PORT": "8080", "DB_PASS": "x"}
    report = clone_report(original, cloned)
    assert report["original_count"] == 3
    assert report["cloned_count"] == 2
    assert "DB_PASS" in report["dropped"]


def test_clone_report_identical():
    report = clone_report(ENV, dict(ENV))
    assert report["dropped"] == []
    assert report["renamed"] == []
