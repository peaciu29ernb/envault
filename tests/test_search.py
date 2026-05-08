"""Tests for envault.search."""

from __future__ import annotations

import pytest

from envault.search import (
    search_keys,
    search_values,
    filter_by_prefix,
    list_keys,
)

SAMPLE: dict[str, str] = {
    "DATABASE_URL": "postgres://localhost/db",
    "DB_PASS": "secret",
    "APP_SECRET_KEY": "abc123",
    "DEBUG": "true",
    "api_token": "tok_xyz",
}


def test_search_keys_glob_case_insensitive():
    result = search_keys(SAMPLE, "DB_*")
    assert "DATABASE_URL" not in result
    assert "DB_PASS" in result


def test_search_keys_glob_wildcard():
    result = search_keys(SAMPLE, "*SECRET*")
    assert "APP_SECRET_KEY" in result


def test_search_keys_case_sensitive_no_match():
    result = search_keys(SAMPLE, "db_*", case_sensitive=True)
    assert result == {}


def test_search_keys_case_sensitive_match():
    result = search_keys(SAMPLE, "api_*", case_sensitive=True)
    assert "api_token" in result


def test_search_keys_regex():
    result = search_keys(SAMPLE, r"^DB", use_regex=True)
    assert "DB_PASS" in result
    assert "DATABASE_URL" not in result


def test_search_keys_regex_case_insensitive():
    result = search_keys(SAMPLE, r"debug", use_regex=True)
    assert "DEBUG" in result


def test_search_values_substring():
    result = search_values(SAMPLE, "secret")
    assert "DB_PASS" in result
    assert "APP_SECRET_KEY" not in result  # value is 'abc123'


def test_search_values_case_insensitive():
    result = search_values(SAMPLE, "SECRET")
    assert "DB_PASS" in result


def test_search_values_regex():
    result = search_values(SAMPLE, r"tok_", use_regex=True)
    assert "api_token" in result


def test_search_values_no_match():
    result = search_values(SAMPLE, "NOTFOUND")
    assert result == {}


def test_filter_by_prefix_db():
    result = filter_by_prefix(SAMPLE, "DB")
    assert "DB_PASS" in result
    assert "DATABASE_URL" not in result


def test_filter_by_prefix_case_insensitive():
    result = filter_by_prefix(SAMPLE, "app")
    assert "APP_SECRET_KEY" in result


def test_filter_by_prefix_no_match():
    assert filter_by_prefix(SAMPLE, "ZZZ") == {}


def test_list_keys_sorted():
    keys = list_keys(SAMPLE)
    assert keys == sorted(SAMPLE.keys())


def test_list_keys_unsorted():
    keys = list_keys(SAMPLE, sort=False)
    assert set(keys) == set(SAMPLE.keys())
