"""Tests for envault.prune."""

from __future__ import annotations

import pytest

from envault.prune import (
    PruneError,
    prune_by_glob,
    prune_by_keys,
    prune_by_regex,
    prune_empty,
    prune_report,
)


SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "TMP_TOKEN": "abc",
    "TMP_SECRET": "xyz",
    "EMPTY_VAL": "",
    "WHITESPACE": "   ",
    "API_KEY": "key123",
}


# ---------------------------------------------------------------------------
# prune_by_keys
# ---------------------------------------------------------------------------

def test_prune_by_keys_removes_listed_keys():
    result, removed = prune_by_keys(SAMPLE, ["DB_HOST", "API_KEY"])
    assert "DB_HOST" not in result
    assert "API_KEY" not in result
    assert set(removed) == {"DB_HOST", "API_KEY"}


def test_prune_by_keys_preserves_other_keys():
    result, _ = prune_by_keys(SAMPLE, ["TMP_TOKEN"])
    assert "DB_HOST" in result
    assert "DB_PORT" in result


def test_prune_by_keys_does_not_mutate_original():
    original = dict(SAMPLE)
    prune_by_keys(original, ["DB_HOST"])
    assert "DB_HOST" in original


def test_prune_by_keys_missing_key_ok_by_default():
    result, removed = prune_by_keys(SAMPLE, ["NONEXISTENT"])
    assert removed == []
    assert result == SAMPLE


def test_prune_by_keys_missing_key_raises_when_not_ok():
    with pytest.raises(PruneError, match="NONEXISTENT"):
        prune_by_keys(SAMPLE, ["NONEXISTENT"], missing_ok=False)


def test_prune_by_keys_empty_list_returns_copy():
    result, removed = prune_by_keys(SAMPLE, [])
    assert result == SAMPLE
    assert removed == []


# ---------------------------------------------------------------------------
# prune_by_glob
# ---------------------------------------------------------------------------

def test_prune_by_glob_removes_matching_prefix():
    result, removed = prune_by_glob(SAMPLE, "TMP_*")
    assert "TMP_TOKEN" not in result
    assert "TMP_SECRET" not in result
    assert set(removed) == {"TMP_TOKEN", "TMP_SECRET"}


def test_prune_by_glob_case_insensitive_by_default():
    result, removed = prune_by_glob(SAMPLE, "tmp_*")
    assert set(removed) == {"TMP_TOKEN", "TMP_SECRET"}


def test_prune_by_glob_case_sensitive_no_match():
    _, removed = prune_by_glob(SAMPLE, "tmp_*", case_sensitive=True)
    assert removed == []


def test_prune_by_glob_no_match_returns_original():
    result, removed = prune_by_glob(SAMPLE, "NOPE_*")
    assert result == SAMPLE
    assert removed == []


# ---------------------------------------------------------------------------
# prune_by_regex
# ---------------------------------------------------------------------------

def test_prune_by_regex_removes_matching_keys():
    result, removed = prune_by_regex(SAMPLE, r"^DB_")
    assert "DB_HOST" not in result
    assert "DB_PORT" not in result
    assert set(removed) == {"DB_HOST", "DB_PORT"}


def test_prune_by_regex_invalid_pattern_raises():
    with pytest.raises(PruneError, match="Invalid regex"):
        prune_by_regex(SAMPLE, "[invalid")


def test_prune_by_regex_no_match_returns_original():
    result, removed = prune_by_regex(SAMPLE, r"^ZZZNOPE")
    assert result == SAMPLE
    assert removed == []


# ---------------------------------------------------------------------------
# prune_empty
# ---------------------------------------------------------------------------

def test_prune_empty_removes_empty_values():
    result, removed = prune_empty(SAMPLE)
    assert "EMPTY_VAL" not in result
    assert "EMPTY_VAL" in removed


def test_prune_empty_removes_whitespace_values_with_strip():
    result, removed = prune_empty(SAMPLE, strip=True)
    assert "WHITESPACE" not in result
    assert "WHITESPACE" in removed


def test_prune_empty_keeps_whitespace_when_no_strip():
    result, removed = prune_empty(SAMPLE, strip=False)
    assert "WHITESPACE" in result
    assert "WHITESPACE" not in removed


def test_prune_empty_keeps_non_empty_values():
    result, _ = prune_empty(SAMPLE)
    assert result["DB_HOST"] == "localhost"


# ---------------------------------------------------------------------------
# prune_report
# ---------------------------------------------------------------------------

def test_prune_report_includes_removed_and_count():
    report = prune_report(["A", "B"])
    assert report["removed"] == ["A", "B"]
    assert report["count"] == 2


def test_prune_report_includes_remaining_when_total_given():
    report = prune_report(["A"], total_before=10)
    assert report["remaining"] == 9


def test_prune_report_no_total_omits_remaining():
    report = prune_report([])
    assert "remaining" not in report
