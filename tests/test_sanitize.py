"""Tests for envault.sanitize."""

import pytest
from envault.sanitize import (
    apply_sanitizer,
    apply_sanitizers,
    sanitize_env,
    list_sanitizers,
    SanitizeError,
)


def test_list_sanitizers_returns_strings():
    names = list_sanitizers()
    assert isinstance(names, list)
    assert "strip" in names
    assert "lower" in names


def test_apply_sanitizer_strip():
    assert apply_sanitizer("  hello  ", "strip") == "hello"


def test_apply_sanitizer_lower():
    assert apply_sanitizer("HELLO", "lower") == "hello"


def test_apply_sanitizer_upper():
    assert apply_sanitizer("hello", "upper") == "HELLO"


def test_apply_sanitizer_strip_quotes_double():
    assert apply_sanitizer('"value"', "strip_quotes") == "value"


def test_apply_sanitizer_strip_quotes_single():
    assert apply_sanitizer("'value'", "strip_quotes") == "value"


def test_apply_sanitizer_collapse_whitespace():
    assert apply_sanitizer("foo   bar\tbaz", "collapse_whitespace") == "foo bar baz"


def test_apply_sanitizer_remove_newlines():
    assert apply_sanitizer("foo\nbar\r", "remove_newlines") == "foobar"


def test_apply_sanitizer_remove_non_printable():
    assert apply_sanitizer("hello\x00world", "remove_non_printable") == "helloworld"


def test_apply_sanitizer_truncate_512():
    long_val = "x" * 600
    assert len(apply_sanitizer(long_val, "truncate_512")) == 512


def test_apply_sanitizer_unknown_raises():
    with pytest.raises(SanitizeError, match="Unknown sanitizer"):
        apply_sanitizer("value", "nonexistent")


def test_apply_sanitizers_chain():
    result = apply_sanitizers('  "HELLO WORLD"  ', ["strip", "strip_quotes", "lower"])
    assert result == "hello world"


def test_apply_sanitizers_empty_list_is_identity():
    assert apply_sanitizers("  value  ", []) == "  value  "


def test_sanitize_env_all_keys():
    env = {"A": "  hello  ", "B": "  world  "}
    result = sanitize_env(env, ["strip"])
    assert result == {"A": "hello", "B": "world"}


def test_sanitize_env_specific_keys_only():
    env = {"A": "  hello  ", "B": "  world  "}
    result = sanitize_env(env, ["strip"], keys=["A"])
    assert result["A"] == "hello"
    assert result["B"] == "  world  "  # untouched


def test_sanitize_env_does_not_mutate_original():
    env = {"A": "  hello  "}
    sanitize_env(env, ["strip"])
    assert env["A"] == "  hello  "


def test_sanitize_env_empty_env():
    assert sanitize_env({}, ["strip"]) == {}
