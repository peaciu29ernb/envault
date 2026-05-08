"""Tests for envault.merge module."""

import pytest
from envault.merge import (
    merge_envs,
    format_merge_report,
    STRATEGY_OURS,
    STRATEGY_THEIRS,
)


def test_merge_adds_new_keys():
    base = {"A": "1"}
    incoming = {"A": "1", "B": "2"}
    merged, conflicts = merge_envs(base, incoming)
    assert merged["B"] == "2"
    assert conflicts == {}


def test_merge_no_conflicts_identical():
    base = {"A": "1", "B": "2"}
    incoming = {"A": "1", "B": "2"}
    merged, conflicts = merge_envs(base, incoming)
    assert merged == base
    assert conflicts == {}


def test_merge_conflict_strategy_ours_keeps_base():
    base = {"KEY": "original"}
    incoming = {"KEY": "updated"}
    merged, conflicts = merge_envs(base, incoming, strategy=STRATEGY_OURS)
    assert merged["KEY"] == "original"
    assert "KEY" in conflicts
    assert conflicts["KEY"] == ["original", "updated"]


def test_merge_conflict_strategy_theirs_takes_incoming():
    base = {"KEY": "original"}
    incoming = {"KEY": "updated"}
    merged, conflicts = merge_envs(base, incoming, strategy=STRATEGY_THEIRS)
    assert merged["KEY"] == "updated"
    assert conflicts["KEY"] == ["original", "updated"]


def test_merge_empty_incoming():
    base = {"A": "1", "B": "2"}
    merged, conflicts = merge_envs(base, {})
    assert merged == base
    assert conflicts == {}


def test_merge_empty_base():
    incoming = {"X": "10", "Y": "20"}
    merged, conflicts = merge_envs({}, incoming)
    assert merged == incoming
    assert conflicts == {}


def test_merge_multiple_conflicts():
    base = {"A": "1", "B": "2", "C": "3"}
    incoming = {"A": "10", "B": "2", "C": "30"}
    merged, conflicts = merge_envs(base, incoming, strategy=STRATEGY_OURS)
    assert set(conflicts.keys()) == {"A", "C"}
    assert merged["A"] == "1"
    assert merged["B"] == "2"
    assert merged["C"] == "3"


def test_merge_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unsupported merge strategy"):
        merge_envs({"A": "1"}, {"A": "2"}, strategy="invalid")


def test_format_merge_report_no_conflicts():
    report = format_merge_report({})
    assert "No conflicts" in report


def test_format_merge_report_with_conflicts_ours():
    conflicts = {"DB_PASS": ["secret", "newsecret"]}
    report = format_merge_report(conflicts, strategy=STRATEGY_OURS)
    assert "DB_PASS" in report
    assert "secret" in report
    assert STRATEGY_OURS in report


def test_format_merge_report_with_conflicts_theirs():
    conflicts = {"API_KEY": ["old", "new"]}
    report = format_merge_report(conflicts, strategy=STRATEGY_THEIRS)
    assert "kept" in report
    assert "new" in report
