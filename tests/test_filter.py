"""Tests for envault.filter."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.filter import (
    FilterError,
    exclude_by_keys,
    filter_by_glob,
    filter_by_keys,
    filter_by_regex,
    filter_by_value,
    filter_env,
    filter_non_empty,
)

SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "API_KEY": "secret",
    "API_URL": "https://example.com",
    "EMPTY_VAR": "",
    "debug_mode": "true",
}


def test_filter_by_keys_returns_only_listed():
    result = filter_by_keys(SAMPLE, ["DB_HOST", "API_KEY"])
    assert result == {"DB_HOST": "localhost", "API_KEY": "secret"}


def test_filter_by_keys_missing_key_ignored():
    result = filter_by_keys(SAMPLE, ["DB_HOST", "MISSING"])
    assert result == {"DB_HOST": "localhost"}


def test_filter_by_keys_empty_list_returns_empty():
    assert filter_by_keys(SAMPLE, []) == {}


def test_exclude_by_keys_removes_listed():
    result = exclude_by_keys(SAMPLE, ["DB_HOST", "DB_PORT"])
    assert "DB_HOST" not in result
    assert "DB_PORT" not in result
    assert "API_KEY" in result


def test_exclude_by_keys_missing_key_no_error():
    result = exclude_by_keys(SAMPLE, ["NONEXISTENT"])
    assert result == SAMPLE


def test_filter_by_glob_prefix():
    result = filter_by_glob(SAMPLE, "DB_*")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_by_glob_case_insensitive_default():
    result = filter_by_glob(SAMPLE, "api_*")
    assert set(result.keys()) == {"API_KEY", "API_URL"}


def test_filter_by_glob_case_sensitive_no_match():
    result = filter_by_glob(SAMPLE, "api_*", case_sensitive=True)
    assert result == {}


def test_filter_by_regex_matches_keys():
    result = filter_by_regex(SAMPLE, r"^DB_")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_by_regex_invalid_pattern_raises():
    with pytest.raises(FilterError, match="Invalid regex"):
        filter_by_regex(SAMPLE, "[invalid")


def test_filter_by_value_matches_values():
    result = filter_by_value(SAMPLE, r"^\d+$")
    assert result == {"DB_PORT": "5432"}


def test_filter_by_value_invalid_pattern_raises():
    with pytest.raises(FilterError):
        filter_by_value(SAMPLE, "[bad")


def test_filter_non_empty_drops_blank_values():
    result = filter_non_empty(SAMPLE)
    assert "EMPTY_VAR" not in result
    assert len(result) == len(SAMPLE) - 1


def test_filter_env_composite_include_and_non_empty():
    env = {"A": "1", "B": "", "C": "3"}
    result = filter_env(env, include_keys=["A", "B", "C"], non_empty=True)
    assert result == {"A": "1", "C": "3"}


def test_filter_env_glob_and_exclude():
    result = filter_env(SAMPLE, glob="DB_*", exclude_keys=["DB_PORT"])
    assert result == {"DB_HOST": "localhost"}


def test_filter_env_no_criteria_returns_copy():
    result = filter_env(SAMPLE)
    assert result == SAMPLE
    assert result is not SAMPLE
