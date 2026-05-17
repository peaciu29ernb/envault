"""Tests for envault.interpolate."""

import pytest
from envault.interpolate import (
    InterpolateError,
    find_references,
    interpolate_env,
)


def test_interpolate_braced_reference():
    env = {"BASE": "https://example.com", "URL": "${BASE}/api"}
    result = interpolate_env(env)
    assert result["URL"] == "https://example.com/api"


def test_interpolate_bare_reference():
    env = {"HOST": "localhost", "DSN": "postgres://$HOST/db"}
    result = interpolate_env(env)
    assert result["DSN"] == "postgres://localhost/db"


def test_interpolate_chained_references():
    env = {
        "PROTO": "https",
        "HOST": "example.com",
        "BASE": "${PROTO}://${HOST}",
        "URL": "${BASE}/v1",
    }
    result = interpolate_env(env)
    assert result["URL"] == "https://example.com/v1"


def test_interpolate_no_references():
    env = {"FOO": "bar", "BAZ": "qux"}
    result = interpolate_env(env)
    assert result == env


def test_interpolate_undefined_non_strict_leaves_unexpanded():
    env = {"URL": "${MISSING}/path"}
    result = interpolate_env(env, strict=False)
    assert result["URL"] == "${MISSING}/path"


def test_interpolate_undefined_strict_raises():
    env = {"URL": "${MISSING}/path"}
    with pytest.raises(InterpolateError, match="Undefined variable"):
        interpolate_env(env, strict=True)


def test_interpolate_circular_reference_raises():
    env = {"A": "${B}", "B": "${A}"}
    with pytest.raises(InterpolateError, match="Circular reference"):
        interpolate_env(env, strict=True)


def test_interpolate_skip_keys_left_unchanged():
    env = {"BASE": "http://localhost", "URL": "${BASE}/api"}
    result = interpolate_env(env, skip_keys=["URL"])
    assert result["URL"] == "${BASE}/api"
    assert result["BASE"] == "http://localhost"


def test_interpolate_does_not_mutate_original():
    env = {"A": "hello", "B": "${A} world"}
    original = dict(env)
    interpolate_env(env)
    assert env == original


def test_interpolate_multiple_refs_in_one_value():
    env = {"USER": "admin", "PASS": "secret", "DSN": "${USER}:${PASS}@host"}
    result = interpolate_env(env)
    assert result["DSN"] == "admin:secret@host"


def test_find_references_braced():
    env = {"URL": "${BASE}/api", "BASE": "http://localhost"}
    refs = find_references(env)
    assert refs["URL"] == ["BASE"]
    assert "BASE" not in refs


def test_find_references_bare():
    env = {"DSN": "postgres://$HOST/db", "HOST": "localhost"}
    refs = find_references(env)
    assert refs["DSN"] == ["HOST"]


def test_find_references_multiple():
    env = {"CONN": "${USER}:${PASS}@${HOST}"}
    refs = find_references(env)
    assert refs["CONN"] == ["USER", "PASS", "HOST"]


def test_find_references_no_refs_returns_empty():
    env = {"FOO": "bar", "BAZ": "qux"}
    refs = find_references(env)
    assert refs == {}


def test_find_references_deduplicates():
    env = {"A": "${X}/${X}"}
    refs = find_references(env)
    assert refs["A"] == ["X"]
