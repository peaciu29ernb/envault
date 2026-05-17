"""Tests for envault.sort."""

from __future__ import annotations

import pytest

from envault.sort import (
    SortError,
    sort_alphabetical,
    sort_by_custom,
    sort_by_key_length,
    sort_by_value_length,
    sort_env,
)


SAMPLE = {"ZEBRA": "last", "APPLE": "first", "MANGO": "mid"}


# ---------------------------------------------------------------------------
# sort_alphabetical
# ---------------------------------------------------------------------------

def test_sort_alphabetical_ascending():
    result = sort_alphabetical(SAMPLE)
    assert list(result.keys()) == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_alphabetical_descending():
    result = sort_alphabetical(SAMPLE, reverse=True)
    assert list(result.keys()) == ["ZEBRA", "MANGO", "APPLE"]


def test_sort_alphabetical_preserves_values():
    result = sort_alphabetical(SAMPLE)
    assert result["APPLE"] == "first"
    assert result["ZEBRA"] == "last"


def test_sort_alphabetical_does_not_mutate_original():
    original = dict(SAMPLE)
    sort_alphabetical(original)
    assert list(original.keys()) == list(SAMPLE.keys())


# ---------------------------------------------------------------------------
# sort_by_key_length
# ---------------------------------------------------------------------------

def test_sort_by_key_length_ascending():
    env = {"AB": "x", "ABCDE": "y", "ABC": "z"}
    result = sort_by_key_length(env)
    assert list(result.keys()) == ["AB", "ABC", "ABCDE"]


def test_sort_by_key_length_descending():
    env = {"AB": "x", "ABCDE": "y", "ABC": "z"}
    result = sort_by_key_length(env, reverse=True)
    assert list(result.keys()) == ["ABCDE", "ABC", "AB"]


# ---------------------------------------------------------------------------
# sort_by_value_length
# ---------------------------------------------------------------------------

def test_sort_by_value_length_ascending():
    env = {"A": "hello world", "B": "hi", "C": "hey"}
    result = sort_by_value_length(env)
    assert list(result.keys()) == ["B", "C", "A"]


def test_sort_by_value_length_descending():
    env = {"A": "hello world", "B": "hi", "C": "hey"}
    result = sort_by_value_length(env, reverse=True)
    assert list(result.keys()) == ["A", "C", "B"]


# ---------------------------------------------------------------------------
# sort_by_custom
# ---------------------------------------------------------------------------

def test_sort_by_custom_basic():
    env = {"C": "3", "A": "1", "B": "2"}
    result = sort_by_custom(env, ["A", "B", "C"])
    assert list(result.keys()) == ["A", "B", "C"]


def test_sort_by_custom_remainder_appended_last():
    env = {"C": "3", "A": "1", "B": "2", "D": "4"}
    result = sort_by_custom(env, ["A", "C"])
    assert list(result.keys())[:2] == ["A", "C"]
    assert "B" in result and "D" in result


def test_sort_by_custom_remainder_first():
    env = {"C": "3", "A": "1", "B": "2", "D": "4"}
    result = sort_by_custom(env, ["A", "C"], remainder_last=False)
    keys = list(result.keys())
    assert keys[-2:] == ["A", "C"]


def test_sort_by_custom_duplicate_order_raises():
    env = {"A": "1", "B": "2"}
    with pytest.raises(SortError, match="duplicate"):
        sort_by_custom(env, ["A", "A"])


# ---------------------------------------------------------------------------
# sort_env dispatcher
# ---------------------------------------------------------------------------

def test_sort_env_alpha_strategy():
    result = sort_env(SAMPLE, "alpha")
    assert list(result.keys()) == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_env_key_length_strategy():
    env = {"AB": "x", "ABCDE": "y", "ABC": "z"}
    result = sort_env(env, "key_length")
    assert list(result.keys()) == ["AB", "ABC", "ABCDE"]


def test_sort_env_value_length_strategy():
    env = {"A": "hello world", "B": "hi", "C": "hey"}
    result = sort_env(env, "value_length")
    assert list(result.keys()) == ["B", "C", "A"]


def test_sort_env_custom_strategy():
    env = {"C": "3", "A": "1", "B": "2"}
    result = sort_env(env, "custom", order=["B", "A", "C"])
    assert list(result.keys()) == ["B", "A", "C"]


def test_sort_env_unknown_strategy_raises():
    with pytest.raises(SortError, match="unknown strategy"):
        sort_env(SAMPLE, "nonexistent")
