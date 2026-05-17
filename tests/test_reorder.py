"""Tests for envault.reorder."""

from __future__ import annotations

import pytest

from envault.reorder import (
    ReorderError,
    move_to_bottom,
    move_to_top,
    reorder_alphabetical,
    reorder_by_list,
    reorder_by_prefix,
)


SAMPLE = {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}


# ---------------------------------------------------------------------------
# reorder_alphabetical
# ---------------------------------------------------------------------------

def test_reorder_alphabetical_ascending():
    result = reorder_alphabetical(SAMPLE)
    assert list(result.keys()) == ["APPLE", "MANGO", "ZEBRA"]


def test_reorder_alphabetical_descending():
    result = reorder_alphabetical(SAMPLE, reverse=True)
    assert list(result.keys()) == ["ZEBRA", "MANGO", "APPLE"]


def test_reorder_alphabetical_preserves_values():
    result = reorder_alphabetical(SAMPLE)
    assert result["APPLE"] == "2"
    assert result["ZEBRA"] == "1"


def test_reorder_alphabetical_empty():
    assert reorder_alphabetical({}) == {}


# ---------------------------------------------------------------------------
# reorder_by_list
# ---------------------------------------------------------------------------

def test_reorder_by_list_basic():
    env = {"C": "3", "A": "1", "B": "2"}
    result = reorder_by_list(env, ["A", "B", "C"])
    assert list(result.keys()) == ["A", "B", "C"]


def test_reorder_by_list_partial_order_appends_rest():
    env = {"C": "3", "A": "1", "B": "2"}
    result = reorder_by_list(env, ["A"], append_rest=True)
    assert list(result.keys())[0] == "A"
    assert set(result.keys()) == {"A", "B", "C"}


def test_reorder_by_list_no_append_rest_raises():
    env = {"A": "1", "B": "2", "C": "3"}
    with pytest.raises(ReorderError, match="append_rest"):
        reorder_by_list(env, ["A", "B"], append_rest=False)


def test_reorder_by_list_skips_missing_keys():
    env = {"A": "1", "B": "2"}
    result = reorder_by_list(env, ["Z", "A", "B"])
    assert list(result.keys()) == ["A", "B"]


def test_reorder_by_list_does_not_mutate_original():
    env = {"B": "2", "A": "1"}
    reorder_by_list(env, ["A", "B"])
    assert list(env.keys()) == ["B", "A"]


# ---------------------------------------------------------------------------
# reorder_by_prefix
# ---------------------------------------------------------------------------

def test_reorder_by_prefix_groups_correctly():
    env = {"DB_HOST": "h", "APP_NAME": "n", "DB_PORT": "5432", "APP_ENV": "prod"}
    result = reorder_by_prefix(env, ["APP_", "DB_"])
    keys = list(result.keys())
    assert keys.index("APP_NAME") < keys.index("DB_HOST")
    assert keys.index("APP_ENV") < keys.index("DB_HOST")


def test_reorder_by_prefix_appends_unmatched():
    env = {"DB_HOST": "h", "OTHER": "x"}
    result = reorder_by_prefix(env, ["DB_"], append_rest=True)
    assert "OTHER" in result
    assert list(result.keys())[-1] == "OTHER"


def test_reorder_by_prefix_no_append_drops_rest():
    env = {"DB_HOST": "h", "OTHER": "x"}
    result = reorder_by_prefix(env, ["DB_"], append_rest=False)
    assert "OTHER" not in result


# ---------------------------------------------------------------------------
# move_to_top / move_to_bottom
# ---------------------------------------------------------------------------

def test_move_to_top_places_keys_first():
    env = {"A": "1", "B": "2", "C": "3"}
    result = move_to_top(env, ["C"])
    assert list(result.keys())[0] == "C"


def test_move_to_top_ignores_missing_keys():
    env = {"A": "1", "B": "2"}
    result = move_to_top(env, ["Z", "A"])
    assert list(result.keys())[0] == "A"
    assert "Z" not in result


def test_move_to_bottom_places_keys_last():
    env = {"A": "1", "B": "2", "C": "3"}
    result = move_to_bottom(env, ["A"])
    assert list(result.keys())[-1] == "A"


def test_move_to_bottom_ignores_missing_keys():
    env = {"A": "1", "B": "2"}
    result = move_to_bottom(env, ["Z", "B"])
    assert list(result.keys())[-1] == "B"
    assert "Z" not in result
