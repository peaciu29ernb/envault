"""Tests for envault.coerce."""

import pytest

from envault.coerce import (
    CoerceError,
    coerce_bool,
    coerce_env,
    coerce_float,
    coerce_int,
    coerce_list,
    coerce_value,
)


# ---------------------------------------------------------------------------
# coerce_bool
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", ["1", "true", "True", "TRUE", "yes", "YES", "on", "ON"])
def test_coerce_bool_truthy(raw):
    assert coerce_bool(raw) is True


@pytest.mark.parametrize("raw", ["0", "false", "False", "FALSE", "no", "NO", "off", "OFF"])
def test_coerce_bool_falsy(raw):
    assert coerce_bool(raw) is False


def test_coerce_bool_invalid_raises():
    with pytest.raises(CoerceError, match="Cannot coerce"):
        coerce_bool("maybe")


# ---------------------------------------------------------------------------
# coerce_int
# ---------------------------------------------------------------------------

def test_coerce_int_valid():
    assert coerce_int("42") == 42


def test_coerce_int_negative():
    assert coerce_int("-7") == -7


def test_coerce_int_whitespace_stripped():
    assert coerce_int("  10  ") == 10


def test_coerce_int_invalid_raises():
    with pytest.raises(CoerceError, match="Cannot coerce"):
        coerce_int("abc")


# ---------------------------------------------------------------------------
# coerce_float
# ---------------------------------------------------------------------------

def test_coerce_float_valid():
    assert coerce_float("3.14") == pytest.approx(3.14)


def test_coerce_float_integer_string():
    assert coerce_float("2") == pytest.approx(2.0)


def test_coerce_float_invalid_raises():
    with pytest.raises(CoerceError, match="Cannot coerce"):
        coerce_float("not-a-number")


# ---------------------------------------------------------------------------
# coerce_list
# ---------------------------------------------------------------------------

def test_coerce_list_basic():
    assert coerce_list("a,b,c") == ["a", "b", "c"]


def test_coerce_list_strips_whitespace():
    assert coerce_list(" a , b , c ") == ["a", "b", "c"]


def test_coerce_list_skips_empty_items():
    assert coerce_list("a,,b") == ["a", "b"]


def test_coerce_list_custom_delimiter():
    assert coerce_list("x|y|z", delimiter="|") == ["x", "y", "z"]


# ---------------------------------------------------------------------------
# coerce_value
# ---------------------------------------------------------------------------

def test_coerce_value_str_passthrough():
    assert coerce_value("hello", "str") == "hello"


def test_coerce_value_unknown_type_raises():
    with pytest.raises(CoerceError, match="Unknown type"):
        coerce_value("42", "datetime")


# ---------------------------------------------------------------------------
# coerce_env
# ---------------------------------------------------------------------------

def test_coerce_env_applies_schema():
    env = {"PORT": "8080", "DEBUG": "true", "RATE": "0.5", "NAME": "app"}
    schema = {"PORT": "int", "DEBUG": "bool", "RATE": "float"}
    result = coerce_env(env, schema)
    assert result["PORT"] == 8080
    assert result["DEBUG"] is True
    assert result["RATE"] == pytest.approx(0.5)
    assert result["NAME"] == "app"  # untouched string


def test_coerce_env_keys_not_in_schema_pass_through():
    env = {"FOO": "bar"}
    result = coerce_env(env, {})
    assert result == {"FOO": "bar"}


def test_coerce_env_strict_raises_on_missing_key():
    env = {"A": "1"}
    schema = {"A": "int", "B": "bool"}
    with pytest.raises(CoerceError, match="missing from env"):
        coerce_env(env, schema, strict=True)


def test_coerce_env_strict_passes_when_all_present():
    env = {"A": "1", "B": "true"}
    schema = {"A": "int", "B": "bool"}
    result = coerce_env(env, schema, strict=True)
    assert result == {"A": 1, "B": True}


def test_coerce_env_list_type():
    env = {"HOSTS": "a,b,c"}
    result = coerce_env(env, {"HOSTS": "list"})
    assert result["HOSTS"] == ["a", "b", "c"]
