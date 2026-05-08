"""Tests for envault.validate module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.validate import (
    ValidationError,
    ValidationResult,
    load_schema,
    validate_env,
)


SIMPLE_SCHEMA = {
    "DATABASE_URL": {"required": True},
    "SECRET_KEY": {"required": True, "pattern": r"[A-Za-z0-9]{16,}"},
    "LOG_LEVEL": {"required": False, "allowed_values": ["DEBUG", "INFO", "WARNING", "ERROR"]},
    "PORT": {"required": False, "pattern": r"\d+"},
}


def test_valid_env_passes():
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abcdefghijklmnop"}
    result = validate_env(env, SIMPLE_SCHEMA)
    assert result.ok
    assert len(result.errors) == 0


def test_missing_required_key_is_error():
    env = {"SECRET_KEY": "abcdefghijklmnop"}
    result = validate_env(env, SIMPLE_SCHEMA)
    assert not result.ok
    keys = [e.key for e in result.errors]
    assert "DATABASE_URL" in keys


def test_missing_optional_key_is_warning():
    env = {"DATABASE_URL": "x", "SECRET_KEY": "abcdefghijklmnop"}
    result = validate_env(env, SIMPLE_SCHEMA)
    assert result.ok  # warnings don't fail
    warn_keys = [w.key for w in result.warnings]
    assert "LOG_LEVEL" in warn_keys
    assert "PORT" in warn_keys


def test_pattern_mismatch_is_error():
    env = {"DATABASE_URL": "x", "SECRET_KEY": "short"}
    result = validate_env(env, SIMPLE_SCHEMA)
    assert not result.ok
    keys = [e.key for e in result.errors]
    assert "SECRET_KEY" in keys


def test_allowed_values_violation_is_error():
    env = {"DATABASE_URL": "x", "SECRET_KEY": "abcdefghijklmnop", "LOG_LEVEL": "VERBOSE"}
    result = validate_env(env, SIMPLE_SCHEMA)
    assert not result.ok
    keys = [e.key for e in result.errors]
    assert "LOG_LEVEL" in keys


def test_allowed_values_valid():
    env = {"DATABASE_URL": "x", "SECRET_KEY": "abcdefghijklmnop", "LOG_LEVEL": "DEBUG"}
    result = validate_env(env, SIMPLE_SCHEMA)
    assert result.ok


def test_validation_error_repr():
    err = ValidationError("FOO", "some message", "error")
    assert "ERROR" in repr(err)
    assert "FOO" in repr(err)


def test_validation_error_to_dict():
    err = ValidationError("BAR", "msg", "warning")
    d = err.to_dict()
    assert d == {"key": "BAR", "message": "msg", "severity": "warning"}


def test_load_schema_reads_json(tmp_path):
    schema = {"API_KEY": {"required": True}}
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(schema))
    loaded = load_schema(p)
    assert loaded == schema


def test_load_schema_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_schema(tmp_path / "nonexistent.json")


def test_all_issues_combines_errors_and_warnings():
    env = {}  # all missing
    result = validate_env(env, SIMPLE_SCHEMA)
    all_keys = [i.key for i in result.all_issues()]
    assert "DATABASE_URL" in all_keys
    assert "LOG_LEVEL" in all_keys
