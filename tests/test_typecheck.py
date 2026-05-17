"""Tests for envault.typecheck."""
from __future__ import annotations

import pytest

from envault.typecheck import (
    TypeCheckError,
    infer_type,
    is_bool,
    is_email,
    is_float,
    is_int,
    is_url,
    typecheck_env,
)


# --- individual predicates ---

def test_is_int_valid():
    assert is_int("42") is True


def test_is_int_negative():
    assert is_int("-7") is True


def test_is_int_invalid():
    assert is_int("3.14") is False


def test_is_float_valid():
    assert is_float("3.14") is True


def test_is_float_int_string_is_also_float():
    assert is_float("10") is True


def test_is_float_invalid():
    assert is_float("hello") is False


def test_is_bool_true_values(value=None):
    for v in ("true", "True", "TRUE", "1", "yes", "on"):
        assert is_bool(v), f"{v!r} should be bool"


def test_is_bool_false_values():
    for v in ("false", "False", "0", "no", "off"):
        assert is_bool(v), f"{v!r} should be bool"


def test_is_bool_invalid():
    assert is_bool("maybe") is False


def test_is_url_http():
    assert is_url("http://example.com") is True


def test_is_url_https():
    assert is_url("https://example.com/path?q=1") is True


def test_is_url_not_url():
    assert is_url("example.com") is False


def test_is_email_valid():
    assert is_email("user@example.com") is True


def test_is_email_invalid():
    assert is_email("not-an-email") is False


# --- infer_type ---

def test_infer_type_bool():
    assert infer_type("true") == "bool"


def test_infer_type_int():
    assert infer_type("42") == "int"


def test_infer_type_float():
    assert infer_type("3.14") == "float"


def test_infer_type_url():
    assert infer_type("https://api.example.com") == "url"


def test_infer_type_email():
    assert infer_type("admin@example.com") == "email"


def test_infer_type_str_fallback():
    assert infer_type("just-a-string") == "str"


# --- typecheck_env ---

def test_typecheck_env_no_violations():
    env = {"PORT": "8080", "DEBUG": "true", "HOST": "localhost"}
    schema = {"PORT": "int", "DEBUG": "bool", "HOST": "str"}
    assert typecheck_env(env, schema) == []


def test_typecheck_env_violation_reported():
    env = {"PORT": "not-a-number"}
    schema = {"PORT": "int"}
    violations = typecheck_env(env, schema)
    assert len(violations) == 1
    assert violations[0]["key"] == "PORT"
    assert violations[0]["expected"] == "int"


def test_typecheck_env_missing_key_skipped():
    env = {"HOST": "localhost"}
    schema = {"PORT": "int"}
    assert typecheck_env(env, schema) == []


def test_typecheck_env_strict_raises():
    env = {"PORT": "bad"}
    schema = {"PORT": "int"}
    with pytest.raises(TypeCheckError, match="PORT"):
        typecheck_env(env, schema, strict=True)


def test_typecheck_env_multiple_violations():
    env = {"PORT": "bad", "URL": "not-a-url"}
    schema = {"PORT": "int", "URL": "url"}
    violations = typecheck_env(env, schema)
    keys = {v["key"] for v in violations}
    assert keys == {"PORT", "URL"}


def test_typecheck_env_unknown_type_skipped():
    env = {"FOO": "bar"}
    schema = {"FOO": "uuid"}
    # unknown type should not raise, just skip
    assert typecheck_env(env, schema) == []
