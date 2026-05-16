"""Tests for envault.cascade."""

import pytest
from envault.cascade import (
    cascade_envs,
    cascade_with_origins,
    list_conflicts,
    effective_value,
)


# ---------------------------------------------------------------------------
# cascade_envs
# ---------------------------------------------------------------------------

def test_cascade_envs_first_wins_by_default():
    base = {"A": "1", "B": "2"}
    override = {"A": "99", "C": "3"}
    result = cascade_envs([base, override])
    assert result["A"] == "1"   # base wins
    assert result["B"] == "2"
    assert result["C"] == "3"   # new key from override


def test_cascade_envs_override_mode_last_wins():
    base = {"A": "1", "B": "2"}
    top = {"A": "99", "C": "3"}
    result = cascade_envs([base, top], override=True)
    assert result["A"] == "99"  # top wins
    assert result["B"] == "2"
    assert result["C"] == "3"


def test_cascade_envs_empty_sources_returns_empty():
    assert cascade_envs([]) == {}


def test_cascade_envs_single_source_passthrough():
    env = {"X": "hello", "Y": "world"}
    assert cascade_envs([env]) == env


def test_cascade_envs_three_layers_first_wins():
    a = {"K": "a"}
    b = {"K": "b", "L": "b"}
    c = {"K": "c", "L": "c", "M": "c"}
    result = cascade_envs([a, b, c])
    assert result == {"K": "a", "L": "b", "M": "c"}


# ---------------------------------------------------------------------------
# cascade_with_origins
# ---------------------------------------------------------------------------

def test_cascade_with_origins_tracks_source():
    sources = [("base", {"A": "1"}), ("prod", {"A": "2", "B": "3"})]
    origins = cascade_with_origins(sources)
    assert origins["A"] == ("base", "1")
    assert origins["B"] == ("prod", "3")


def test_cascade_with_origins_override_mode():
    sources = [("base", {"A": "1"}), ("prod", {"A": "2"})]
    origins = cascade_with_origins(sources, override=True)
    assert origins["A"] == ("prod", "2")


# ---------------------------------------------------------------------------
# list_conflicts
# ---------------------------------------------------------------------------

def test_list_conflicts_detects_differing_values():
    sources = [
        ("base", {"DB_HOST": "localhost", "PORT": "5432"}),
        ("prod", {"DB_HOST": "prod.db.example.com", "PORT": "5432"}),
    ]
    conflicts = list_conflicts(sources)
    assert "DB_HOST" in conflicts
    assert "PORT" not in conflicts  # same value in both


def test_list_conflicts_no_conflicts_when_identical():
    sources = [("a", {"X": "1"}), ("b", {"X": "1"})]
    assert list_conflicts(sources) == {}


def test_list_conflicts_unique_keys_not_flagged():
    sources = [("a", {"X": "1"}), ("b", {"Y": "2"})]
    assert list_conflicts(sources) == {}


# ---------------------------------------------------------------------------
# effective_value
# ---------------------------------------------------------------------------

def test_effective_value_returns_first_source():
    sources = [("base", {"KEY": "base_val"}), ("env", {"KEY": "env_val"})]
    result = effective_value("KEY", sources)
    assert result == ("base", "base_val")


def test_effective_value_override_returns_last_source():
    sources = [("base", {"KEY": "base_val"}), ("env", {"KEY": "env_val"})]
    result = effective_value("KEY", sources, override=True)
    assert result == ("env", "env_val")


def test_effective_value_missing_key_returns_none():
    sources = [("base", {"A": "1"})]
    assert effective_value("MISSING", sources) is None
