"""Tests for envault.resolve."""

import pytest

from envault.resolve import (
    ResolveResult,
    resolve_key,
    resolve_all,
    unresolved_keys,
)


SOURCES = [
    ("vault", {"DB_HOST": "localhost", "DB_PORT": "5432"}),
    ("profile", {"DB_HOST": "prod.db", "API_KEY": "abc123"}),
    ("override", {"LOG_LEVEL": "DEBUG"}),
]


def test_resolve_key_first_source_wins():
    result = resolve_key("DB_HOST", SOURCES)
    assert result.value == "localhost"
    assert result.source == "vault"
    assert result.resolved is True


def test_resolve_key_falls_through_to_second_source():
    result = resolve_key("API_KEY", SOURCES)
    assert result.value == "abc123"
    assert result.source == "profile"


def test_resolve_key_found_in_third_source():
    result = resolve_key("LOG_LEVEL", SOURCES)
    assert result.value == "DEBUG"
    assert result.source == "override"


def test_resolve_key_not_found_returns_unresolved():
    result = resolve_key("MISSING_KEY", SOURCES)
    assert result.resolved is False
    assert result.value is None
    assert result.source is None


def test_resolve_key_uses_default_when_missing():
    result = resolve_key("MISSING_KEY", SOURCES, default="fallback")
    assert result.resolved is True
    assert result.value == "fallback"
    assert result.source == "default"


def test_resolve_key_default_not_used_when_found():
    result = resolve_key("DB_PORT", SOURCES, default="9999")
    assert result.value == "5432"
    assert result.source == "vault"


def test_resolve_key_empty_sources_returns_unresolved():
    result = resolve_key("DB_HOST", [])
    assert result.resolved is False


def test_resolve_result_to_dict():
    r = ResolveResult(key="FOO", value="bar", source="vault", resolved=True)
    d = r.to_dict()
    assert d == {"key": "FOO", "value": "bar", "source": "vault", "resolved": True}


def test_resolve_all_returns_all_keys():
    keys = ["DB_HOST", "API_KEY", "MISSING"]
    results = resolve_all(keys, SOURCES)
    assert set(results.keys()) == {"DB_HOST", "API_KEY", "MISSING"}
    assert results["DB_HOST"].resolved is True
    assert results["MISSING"].resolved is False


def test_resolve_all_applies_defaults():
    keys = ["DB_HOST", "MISSING"]
    results = resolve_all(keys, SOURCES, defaults={"MISSING": "default_val"})
    assert results["MISSING"].value == "default_val"
    assert results["MISSING"].source == "default"


def test_unresolved_keys_returns_missing():
    keys = ["DB_HOST", "API_KEY", "NOPE", "ALSO_NOPE"]
    results = resolve_all(keys, SOURCES)
    missing = unresolved_keys(results)
    assert set(missing) == {"NOPE", "ALSO_NOPE"}


def test_unresolved_keys_empty_when_all_resolved():
    keys = ["DB_HOST", "DB_PORT"]
    results = resolve_all(keys, SOURCES)
    assert unresolved_keys(results) == []
