"""Tests for envault.ttl — key TTL / expiry tracking."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envault.ttl import (
    expired_keys,
    get_expiry,
    is_expired,
    list_ttl,
    remove_ttl,
    set_ttl,
)


@pytest.fixture()
def ttl_dir(tmp_path: Path) -> Path:
    return tmp_path / "ttl"


def test_set_ttl_returns_future_timestamp(ttl_dir):
    before = time.time()
    expiry = set_ttl("proj", "API_KEY", 60, base_dir=ttl_dir)
    assert expiry > before
    assert expiry <= time.time() + 61


def test_get_expiry_returns_stored_value(ttl_dir):
    expiry = set_ttl("proj", "TOKEN", 120, base_dir=ttl_dir)
    assert get_expiry("proj", "TOKEN", base_dir=ttl_dir) == pytest.approx(expiry)


def test_get_expiry_missing_key_returns_none(ttl_dir):
    assert get_expiry("proj", "MISSING", base_dir=ttl_dir) is None


def test_is_expired_future_key_returns_false(ttl_dir):
    set_ttl("proj", "DB_PASS", 9999, base_dir=ttl_dir)
    assert is_expired("proj", "DB_PASS", base_dir=ttl_dir) is False


def test_is_expired_past_key_returns_true(ttl_dir):
    set_ttl("proj", "OLD_KEY", -1, base_dir=ttl_dir)  # already expired
    assert is_expired("proj", "OLD_KEY", base_dir=ttl_dir) is True


def test_is_expired_no_ttl_returns_false(ttl_dir):
    assert is_expired("proj", "NO_TTL_KEY", base_dir=ttl_dir) is False


def test_remove_ttl_returns_true_when_present(ttl_dir):
    set_ttl("proj", "TEMP", 30, base_dir=ttl_dir)
    assert remove_ttl("proj", "TEMP", base_dir=ttl_dir) is True
    assert get_expiry("proj", "TEMP", base_dir=ttl_dir) is None


def test_remove_ttl_returns_false_when_absent(ttl_dir):
    assert remove_ttl("proj", "GHOST", base_dir=ttl_dir) is False


def test_expired_keys_returns_only_expired(ttl_dir):
    set_ttl("proj", "ALIVE", 9999, base_dir=ttl_dir)
    set_ttl("proj", "DEAD", -1, base_dir=ttl_dir)
    result = expired_keys("proj", base_dir=ttl_dir)
    assert "DEAD" in result
    assert "ALIVE" not in result


def test_expired_keys_empty_when_none_expired(ttl_dir):
    set_ttl("proj", "A", 9999, base_dir=ttl_dir)
    assert expired_keys("proj", base_dir=ttl_dir) == []


def test_list_ttl_returns_all_entries(ttl_dir):
    set_ttl("proj", "K1", 10, base_dir=ttl_dir)
    set_ttl("proj", "K2", 20, base_dir=ttl_dir)
    entries = list_ttl("proj", base_dir=ttl_dir)
    assert set(entries.keys()) == {"K1", "K2"}


def test_list_ttl_empty_project(ttl_dir):
    assert list_ttl("empty_proj", base_dir=ttl_dir) == {}


def test_set_ttl_overwrites_existing(ttl_dir):
    set_ttl("proj", "KEY", 10, base_dir=ttl_dir)
    new_expiry = set_ttl("proj", "KEY", 9999, base_dir=ttl_dir)
    assert get_expiry("proj", "KEY", base_dir=ttl_dir) == pytest.approx(new_expiry)
    assert not is_expired("proj", "KEY", base_dir=ttl_dir)
