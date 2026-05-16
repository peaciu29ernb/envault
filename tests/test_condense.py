"""Tests for envault.condense."""

import pytest

from envault.condense import (
    condense,
    deduplicate_values,
    drop_empty_values,
    find_duplicate_values,
)


# ---------------------------------------------------------------------------
# find_duplicate_values
# ---------------------------------------------------------------------------

def test_find_duplicate_values_identifies_shared_values():
    env = {"A": "same", "B": "same", "C": "unique"}
    dupes = find_duplicate_values(env)
    assert "same" in dupes
    assert set(dupes["same"]) == {"A", "B"}
    assert "unique" not in dupes


def test_find_duplicate_values_empty_env():
    assert find_duplicate_values({}) == {}


def test_find_duplicate_values_no_duplicates():
    env = {"X": "1", "Y": "2", "Z": "3"}
    assert find_duplicate_values(env) == {}


def test_find_duplicate_values_three_keys_same_value():
    env = {"A": "v", "B": "v", "C": "v"}
    dupes = find_duplicate_values(env)
    assert set(dupes["v"]) == {"A", "B", "C"}


# ---------------------------------------------------------------------------
# drop_empty_values
# ---------------------------------------------------------------------------

def test_drop_empty_values_removes_empty():
    env = {"A": "hello", "B": "", "C": "world"}
    filtered, removed = drop_empty_values(env)
    assert "B" not in filtered
    assert "B" in removed
    assert filtered == {"A": "hello", "C": "world"}


def test_drop_empty_values_nothing_to_remove():
    env = {"A": "1", "B": "2"}
    filtered, removed = drop_empty_values(env)
    assert filtered == env
    assert removed == []


def test_drop_empty_values_all_empty():
    env = {"A": "", "B": ""}
    filtered, removed = drop_empty_values(env)
    assert filtered == {}
    assert set(removed) == {"A", "B"}


# ---------------------------------------------------------------------------
# deduplicate_values
# ---------------------------------------------------------------------------

def test_deduplicate_keeps_first_by_default():
    env = {"B_KEY": "same", "A_KEY": "same"}
    result, removed = deduplicate_values(env)
    # "A_KEY" sorts before "B_KEY", so "B_KEY" is removed
    assert "A_KEY" in result
    assert "B_KEY" in removed


def test_deduplicate_keep_last():
    env = {"A_KEY": "same", "B_KEY": "same"}
    result, removed = deduplicate_values(env, keep="last")
    assert "B_KEY" in result
    assert "A_KEY" in removed


def test_deduplicate_no_duplicates_unchanged():
    env = {"A": "1", "B": "2"}
    result, removed = deduplicate_values(env)
    assert result == env
    assert removed == []


# ---------------------------------------------------------------------------
# condense (integration)
# ---------------------------------------------------------------------------

def test_condense_removes_empty_and_duplicates():
    env = {
        "ALPHA": "shared",
        "BETA": "shared",
        "GAMMA": "",
        "DELTA": "unique",
    }
    result, report = condense(env)
    assert "GAMMA" not in result
    assert "GAMMA" in report["empty_removed"]
    # One of ALPHA/BETA should be removed
    assert len(report["duplicate_removed"]) == 1
    assert "DELTA" in result


def test_condense_remove_empty_only():
    env = {"A": "", "B": "val", "C": "val"}
    result, report = condense(env, remove_empty=True, deduplicate=False)
    assert "A" not in result
    assert report["empty_removed"] == ["A"]
    assert report["duplicate_removed"] == []
    assert result == {"B": "val", "C": "val"}


def test_condense_deduplicate_only():
    env = {"A": "", "B": "val", "C": "val"}
    result, report = condense(env, remove_empty=False, deduplicate=True)
    assert "A" in result  # empty not removed
    assert report["empty_removed"] == []
    assert len(report["duplicate_removed"]) == 1


def test_condense_empty_env():
    result, report = condense({})
    assert result == {}
    assert report["empty_removed"] == []
    assert report["duplicate_removed"] == []
