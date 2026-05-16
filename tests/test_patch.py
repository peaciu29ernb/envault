"""Tests for envault.patch."""

import pytest

from envault.patch import PatchError, apply_patch, build_patch


# ---------------------------------------------------------------------------
# apply_patch — set
# ---------------------------------------------------------------------------

def test_apply_patch_set_new_key():
    env = {"A": "1"}
    result = apply_patch(env, [{"op": "set", "key": "B", "value": "2"}])
    assert result == {"A": "1", "B": "2"}


def test_apply_patch_set_overwrites_existing():
    env = {"A": "old"}
    result = apply_patch(env, [{"op": "set", "key": "A", "value": "new"}])
    assert result["A"] == "new"


def test_apply_patch_set_does_not_mutate_original():
    env = {"A": "1"}
    apply_patch(env, [{"op": "set", "key": "B", "value": "2"}])
    assert "B" not in env


# ---------------------------------------------------------------------------
# apply_patch — delete
# ---------------------------------------------------------------------------

def test_apply_patch_delete_existing_key():
    env = {"A": "1", "B": "2"}
    result = apply_patch(env, [{"op": "delete", "key": "A"}])
    assert result == {"B": "2"}


def test_apply_patch_delete_missing_key_raises():
    env = {"A": "1"}
    with pytest.raises(PatchError, match="not found"):
        apply_patch(env, [{"op": "delete", "key": "MISSING"}])


# ---------------------------------------------------------------------------
# apply_patch — rename
# ---------------------------------------------------------------------------

def test_apply_patch_rename_moves_value():
    env = {"OLD": "val", "OTHER": "x"}
    result = apply_patch(env, [{"op": "rename", "from": "OLD", "to": "NEW"}])
    assert "NEW" in result
    assert result["NEW"] == "val"
    assert "OLD" not in result


def test_apply_patch_rename_missing_source_raises():
    with pytest.raises(PatchError, match="source key"):
        apply_patch({}, [{"op": "rename", "from": "GHOST", "to": "NEW"}])


def test_apply_patch_rename_existing_dest_raises():
    env = {"A": "1", "B": "2"}
    with pytest.raises(PatchError, match="destination key"):
        apply_patch(env, [{"op": "rename", "from": "A", "to": "B"}])


# ---------------------------------------------------------------------------
# apply_patch — ordering & unknown op
# ---------------------------------------------------------------------------

def test_apply_patch_multiple_ops_applied_in_order():
    env = {"A": "1"}
    patch = [
        {"op": "set", "key": "B", "value": "2"},
        {"op": "delete", "key": "A"},
        {"op": "rename", "from": "B", "to": "C"},
    ]
    result = apply_patch(env, patch)
    assert result == {"C": "2"}


def test_apply_patch_unknown_op_raises():
    with pytest.raises(PatchError, match="unknown operation"):
        apply_patch({}, [{"op": "upsert", "key": "X", "value": "y"}])


def test_apply_patch_missing_field_raises():
    with pytest.raises(PatchError, match="missing required field"):
        apply_patch({}, [{"op": "set", "key": "X"}])  # no 'value'


def test_apply_patch_empty_patch_returns_copy():
    env = {"A": "1"}
    result = apply_patch(env, [])
    assert result == env
    assert result is not env


# ---------------------------------------------------------------------------
# build_patch
# ---------------------------------------------------------------------------

def test_build_patch_detects_added_key():
    ops = build_patch({"A": "1"}, {"A": "1", "B": "2"})
    assert {"op": "set", "key": "B", "value": "2"} in ops


def test_build_patch_detects_changed_value():
    ops = build_patch({"A": "old"}, {"A": "new"})
    assert {"op": "set", "key": "A", "value": "new"} in ops


def test_build_patch_detects_deleted_key():
    ops = build_patch({"A": "1", "B": "2"}, {"A": "1"})
    assert {"op": "delete", "key": "B"} in ops


def test_build_patch_no_changes_returns_empty():
    env = {"A": "1", "B": "2"}
    assert build_patch(env, env) == []


def test_build_patch_roundtrip():
    before = {"X": "1", "Y": "old"}
    after = {"Y": "new", "Z": "3"}
    ops = build_patch(before, after)
    result = apply_patch(before, ops)
    assert result == after
