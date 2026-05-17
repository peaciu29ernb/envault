"""Tests for envault.dedup."""

import pytest

from envault.dedup import (
    DedupError,
    dedup_keys,
    dedup_report,
    find_duplicate_keys,
)


# ---------------------------------------------------------------------------
# find_duplicate_keys
# ---------------------------------------------------------------------------

def test_find_duplicate_keys_no_overlap():
    a = {"FOO": "1"}
    b = {"BAR": "2"}
    assert find_duplicate_keys(a, b) == {}


def test_find_duplicate_keys_single_overlap():
    a = {"FOO": "1", "BAZ": "x"}
    b = {"FOO": "2", "QUX": "y"}
    result = find_duplicate_keys(a, b)
    assert result == {"FOO": [0, 1]}


def test_find_duplicate_keys_multiple_overlaps():
    a = {"A": "1", "B": "2"}
    b = {"A": "3", "B": "4"}
    result = find_duplicate_keys(a, b)
    assert set(result.keys()) == {"A", "B"}


def test_find_duplicate_keys_three_sources():
    a = {"X": "1"}
    b = {"X": "2"}
    c = {"X": "3"}
    result = find_duplicate_keys(a, b, c)
    assert result == {"X": [0, 1, 2]}


def test_find_duplicate_keys_unique_across_all():
    a = {"A": "1"}
    b = {"B": "2"}
    c = {"C": "3"}
    assert find_duplicate_keys(a, b, c) == {}


# ---------------------------------------------------------------------------
# dedup_keys – strategy: first
# ---------------------------------------------------------------------------

def test_dedup_keys_first_wins():
    a = {"FOO": "from_a", "ONLY_A": "yes"}
    b = {"FOO": "from_b", "ONLY_B": "yes"}
    result = dedup_keys(a, b, strategy="first")
    assert result["FOO"] == "from_a"
    assert result["ONLY_A"] == "yes"
    assert result["ONLY_B"] == "yes"


def test_dedup_keys_first_is_default():
    a = {"K": "a"}
    b = {"K": "b"}
    assert dedup_keys(a, b)["K"] == "a"


# ---------------------------------------------------------------------------
# dedup_keys – strategy: last
# ---------------------------------------------------------------------------

def test_dedup_keys_last_wins():
    a = {"FOO": "from_a"}
    b = {"FOO": "from_b"}
    result = dedup_keys(a, b, strategy="last")
    assert result["FOO"] == "from_b"


def test_dedup_keys_last_three_sources():
    a = {"K": "1"}
    b = {"K": "2"}
    c = {"K": "3"}
    result = dedup_keys(a, b, c, strategy="last")
    assert result["K"] == "3"


# ---------------------------------------------------------------------------
# dedup_keys – strategy: error
# ---------------------------------------------------------------------------

def test_dedup_keys_error_raises_on_duplicate():
    a = {"FOO": "1"}
    b = {"FOO": "2"}
    with pytest.raises(DedupError, match="FOO"):
        dedup_keys(a, b, strategy="error")


def test_dedup_keys_error_passes_when_no_duplicates():
    a = {"A": "1"}
    b = {"B": "2"}
    result = dedup_keys(a, b, strategy="error")
    assert result == {"A": "1", "B": "2"}


def test_dedup_keys_unknown_strategy_raises():
    with pytest.raises(ValueError, match="Unknown dedup strategy"):
        dedup_keys({"A": "1"}, strategy="bogus")


# ---------------------------------------------------------------------------
# dedup_report
# ---------------------------------------------------------------------------

def test_dedup_report_empty_when_no_duplicates():
    a = {"A": "1"}
    b = {"B": "2"}
    assert dedup_report(a, b) == []


def test_dedup_report_contains_duplicate_info():
    a = {"FOO": "from_a", "BAR": "x"}
    b = {"FOO": "from_b", "BAR": "y"}
    report = dedup_report(a, b)
    keys = [entry[0] for entry in report]
    assert "FOO" in keys
    assert "BAR" in keys


def test_dedup_report_values_by_source():
    a = {"K": "val_a"}
    b = {"K": "val_b"}
    report = dedup_report(a, b)
    assert len(report) == 1
    key, by_source = report[0]
    assert key == "K"
    assert by_source == {0: "val_a", 1: "val_b"}


def test_dedup_report_sorted_by_key():
    a = {"Z": "1", "A": "2"}
    b = {"Z": "3", "A": "4"}
    report = dedup_report(a, b)
    keys = [entry[0] for entry in report]
    assert keys == sorted(keys)
