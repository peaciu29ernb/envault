"""Tests for envault.normalize."""

import pytest

from envault.normalize import (
    NormalizeError,
    normalize_key,
    normalize_value,
    normalize_env,
)


# ---------------------------------------------------------------------------
# normalize_key
# ---------------------------------------------------------------------------

def test_normalize_key_uppercases():
    assert normalize_key("my_key") == "MY_KEY"


def test_normalize_key_strips_whitespace():
    assert normalize_key("  foo  ") == "FOO"


def test_normalize_key_replaces_hyphens():
    assert normalize_key("my-key") == "MY_KEY"


def test_normalize_key_no_upper():
    assert normalize_key("My_Key", upper=False) == "My_Key"


def test_normalize_key_no_replace_hyphens():
    assert normalize_key("my-key", replace_hyphens=False) == "MY-KEY"


def test_normalize_key_empty_raises():
    with pytest.raises(NormalizeError):
        normalize_key("   ")


def test_normalize_key_already_upper():
    assert normalize_key("DATABASE_URL") == "DATABASE_URL"


# ---------------------------------------------------------------------------
# normalize_value
# ---------------------------------------------------------------------------

def test_normalize_value_strips_by_default():
    assert normalize_value("  hello  ") == "hello"


def test_normalize_value_no_strip():
    assert normalize_value("  hello  ", strip=False) == "  hello  "


def test_normalize_value_collapse_whitespace():
    assert normalize_value("hello   world", collapse_whitespace=True) == "hello world"


def test_normalize_value_collapse_and_strip():
    assert normalize_value("  hello   world  ", collapse_whitespace=True) == "hello world"


def test_normalize_value_empty_string():
    assert normalize_value("") == ""


# ---------------------------------------------------------------------------
# normalize_env
# ---------------------------------------------------------------------------

def test_normalize_env_basic():
    env = {"db_host": "  localhost  ", "db-port": "5432"}
    result = normalize_env(env)
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_normalize_env_returns_new_dict():
    env = {"KEY": "value"}
    result = normalize_env(env)
    assert result is not env


def test_normalize_env_conflict_error():
    env = {"my-key": "a", "my_key": "b"}
    with pytest.raises(NormalizeError, match="conflict"):
        normalize_env(env, on_conflict="error")


def test_normalize_env_conflict_first():
    # dict preserves insertion order in Python 3.7+
    env = {"my-key": "first", "my_key": "second"}
    result = normalize_env(env, on_conflict="first")
    assert result["MY_KEY"] == "first"


def test_normalize_env_conflict_last():
    env = {"my-key": "first", "my_key": "second"}
    result = normalize_env(env, on_conflict="last")
    assert result["MY_KEY"] == "second"


def test_normalize_env_invalid_on_conflict():
    with pytest.raises(ValueError):
        normalize_env({}, on_conflict="ignore")


def test_normalize_env_empty():
    assert normalize_env({}) == {}


def test_normalize_env_collapse_values():
    env = {"MESSAGE": "hello   world"}
    result = normalize_env(env, collapse_whitespace=True)
    assert result["MESSAGE"] == "hello world"
