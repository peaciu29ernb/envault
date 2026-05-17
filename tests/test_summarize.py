"""Tests for envault.summarize."""

from __future__ import annotations

import pytest

from envault.summarize import (
    average_value_length,
    count_empty,
    count_keys,
    count_sensitive,
    longest_key,
    summarize,
)


ENV = {
    "DATABASE_URL": "postgres://localhost/db",
    "API_KEY": "abc123",
    "SECRET_TOKEN": "s3cr3t",
    "DEBUG": "",
    "PORT": "8080",
}


def test_count_keys_returns_total():
    assert count_keys(ENV) == 5


def test_count_keys_empty_env():
    assert count_keys({}) == 0


def test_count_empty_finds_blank_values():
    assert count_empty(ENV) == 1


def test_count_empty_none_empty():
    assert count_empty({"A": "1", "B": "2"}) == 0


def test_count_sensitive_matches_known_patterns():
    # API_KEY and SECRET_TOKEN should both be flagged
    assert count_sensitive(ENV) == 2


def test_count_sensitive_empty_env():
    assert count_sensitive({}) == 0


def test_count_sensitive_no_sensitive_keys():
    assert count_sensitive({"DEBUG": "true", "PORT": "8080"}) == 0


def test_average_value_length_empty_env():
    assert average_value_length({}) == 0.0


def test_average_value_length_single_key():
    assert average_value_length({"A": "hello"}) == 5.0


def test_average_value_length_multiple_keys():
    env = {"A": "ab", "B": "abcd"}
    assert average_value_length(env) == 3.0


def test_longest_key_empty_env():
    assert longest_key({}) is None


def test_longest_key_returns_correct_key():
    assert longest_key({"SHORT": "1", "VERY_LONG_KEY_NAME": "2"}) == "VERY_LONG_KEY_NAME"


def test_longest_key_single_entry():
    assert longest_key({"ONLY": "val"}) == "ONLY"


def test_summarize_returns_all_fields():
    result = summarize(ENV)
    assert "total_keys" in result
    assert "empty_values" in result
    assert "non_empty_values" in result
    assert "sensitive_keys" in result
    assert "average_value_length" in result
    assert "longest_key" in result


def test_summarize_values_are_consistent():
    result = summarize(ENV)
    assert result["total_keys"] == result["empty_values"] + result["non_empty_values"]


def test_summarize_empty_env():
    result = summarize({})
    assert result["total_keys"] == 0
    assert result["longest_key"] is None
    assert result["average_value_length"] == 0.0
