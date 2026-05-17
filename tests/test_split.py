"""Tests for envault.split."""

from __future__ import annotations

import pytest

from envault.split import (
    SplitError,
    split_by_glob,
    split_by_prefix,
    split_by_regex,
)


SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "REDIS_URL": "redis://localhost",
    "APP_DEBUG": "true",
    "SECRET_KEY": "abc123",
}


# ---------------------------------------------------------------------------
# split_by_prefix
# ---------------------------------------------------------------------------

def test_split_by_prefix_basic():
    result = split_by_prefix(SAMPLE, ["DB_", "REDIS_"])
    assert result["DB_"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}
    assert result["REDIS_"] == {"REDIS_URL": "redis://localhost"}
    assert result["__rest__"] == {"APP_DEBUG": "true", "SECRET_KEY": "abc123"}


def test_split_by_prefix_strip():
    result = split_by_prefix(SAMPLE, ["DB_"], strip_prefix=True)
    assert "HOST" in result["DB_"]
    assert "PORT" in result["DB_"]


def test_split_by_prefix_no_remainder():
    result = split_by_prefix(SAMPLE, ["DB_"], remainder_key=None)
    assert "__rest__" not in result


def test_split_by_prefix_custom_remainder():
    result = split_by_prefix(SAMPLE, ["DB_"], remainder_key="other")
    assert "other" in result
    assert "APP_DEBUG" in result["other"]


def test_split_by_prefix_first_match_wins():
    env = {"DB_HOST": "h", "DB_REDIS_EXTRA": "x"}
    result = split_by_prefix(env, ["DB_", "DB_REDIS_"])
    assert "DB_REDIS_EXTRA" in result["DB_"]
    assert result["DB_REDIS_"] == {}


def test_split_by_prefix_empty_env():
    result = split_by_prefix({}, ["DB_"])
    assert result["DB_"] == {}
    assert result["__rest__"] == {}


# ---------------------------------------------------------------------------
# split_by_glob
# ---------------------------------------------------------------------------

def test_split_by_glob_wildcard():
    result = split_by_glob(SAMPLE, {"db": "DB_*", "redis": "REDIS_*"})
    assert result["db"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}
    assert result["redis"] == {"REDIS_URL": "redis://localhost"}


def test_split_by_glob_no_rest():
    result = split_by_glob(SAMPLE, {"db": "DB_*"}, remainder_key=None)
    assert "__rest__" not in result


def test_split_by_glob_question_mark():
    env = {"KEY_A": "1", "KEY_B": "2", "KEY_CC": "3"}
    result = split_by_glob(env, {"single": "KEY_?"})
    assert result["single"] == {"KEY_A": "1", "KEY_B": "2"}
    assert result["__rest__"] == {"KEY_CC": "3"}


def test_split_by_glob_empty_env():
    result = split_by_glob({}, {"x": "X_*"})
    assert result["x"] == {}
    assert result["__rest__"] == {}


# ---------------------------------------------------------------------------
# split_by_regex
# ---------------------------------------------------------------------------

def test_split_by_regex_basic():
    result = split_by_regex(SAMPLE, {"db": r"^DB_", "redis": r"^REDIS_"})
    assert result["db"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}
    assert result["redis"] == {"REDIS_URL": "redis://localhost"}


def test_split_by_regex_partial_match():
    env = {"MY_DB_HOST": "h", "OTHER": "x"}
    result = split_by_regex(env, {"db": r"DB"})
    assert "MY_DB_HOST" in result["db"]


def test_split_by_regex_invalid_pattern_raises():
    with pytest.raises(SplitError, match="Invalid regex"):
        split_by_regex(SAMPLE, {"bad": r"[invalid"})


def test_split_by_regex_no_rest():
    result = split_by_regex(SAMPLE, {"all": r".*"}, remainder_key=None)
    assert "__rest__" not in result
    assert len(result["all"]) == len(SAMPLE)


def test_split_by_regex_empty_env():
    result = split_by_regex({}, {"x": r"^X"})
    assert result["x"] == {}
    assert result["__rest__"] == {}
