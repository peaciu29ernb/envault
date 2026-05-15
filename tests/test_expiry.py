"""Tests for envault/expiry.py"""

from __future__ import annotations

import time

import pytest

from envault.expiry import (
    get_expiry,
    is_expired,
    list_expired,
    list_expiries,
    remove_expiry,
    set_expiry,
    set_expiry_in,
)


@pytest.fixture()
def expiry_dir(tmp_path):
    return tmp_path / "expiry"


def test_set_expiry_returns_timestamp(expiry_dir):
    ts = time.time() + 3600
    result = set_expiry("myapp", "API_KEY", ts, base_dir=expiry_dir)
    assert result == pytest.approx(ts)


def test_get_expiry_returns_stored_value(expiry_dir):
    ts = time.time() + 7200
    set_expiry("myapp", "DB_PASS", ts, base_dir=expiry_dir)
    assert get_expiry("myapp", "DB_PASS", base_dir=expiry_dir) == pytest.approx(ts)


def test_get_expiry_missing_key_returns_none(expiry_dir):
    assert get_expiry("myapp", "NONEXISTENT", base_dir=expiry_dir) is None


def test_set_expiry_in_stores_future_timestamp(expiry_dir):
    before = time.time()
    ts = set_expiry_in("myapp", "TOKEN", 60, base_dir=expiry_dir)
    after = time.time()
    assert before + 60 <= ts <= after + 60


def test_is_expired_future_key_returns_false(expiry_dir):
    set_expiry("myapp", "API_KEY", time.time() + 9999, base_dir=expiry_dir)
    assert is_expired("myapp", "API_KEY", base_dir=expiry_dir) is False


def test_is_expired_past_key_returns_true(expiry_dir):
    set_expiry("myapp", "OLD_KEY", time.time() - 1, base_dir=expiry_dir)
    assert is_expired("myapp", "OLD_KEY", base_dir=expiry_dir) is True


def test_is_expired_missing_key_returns_false(expiry_dir):
    assert is_expired("myapp", "GHOST", base_dir=expiry_dir) is False


def test_remove_expiry_returns_true(expiry_dir):
    set_expiry("myapp", "API_KEY", time.time() + 100, base_dir=expiry_dir)
    assert remove_expiry("myapp", "API_KEY", base_dir=expiry_dir) is True
    assert get_expiry("myapp", "API_KEY", base_dir=expiry_dir) is None


def test_remove_expiry_missing_returns_false(expiry_dir):
    assert remove_expiry("myapp", "GHOST", base_dir=expiry_dir) is False


def test_list_expired_returns_only_past_keys(expiry_dir):
    set_expiry("proj", "PAST", time.time() - 5, base_dir=expiry_dir)
    set_expiry("proj", "FUTURE", time.time() + 5000, base_dir=expiry_dir)
    expired = list_expired("proj", base_dir=expiry_dir)
    assert "PAST" in expired
    assert "FUTURE" not in expired


def test_list_expiries_returns_all_entries(expiry_dir):
    ts1 = time.time() + 100
    ts2 = time.time() + 200
    set_expiry("proj", "K1", ts1, base_dir=expiry_dir)
    set_expiry("proj", "K2", ts2, base_dir=expiry_dir)
    result = list_expiries("proj", base_dir=expiry_dir)
    assert set(result.keys()) == {"K1", "K2"}
    assert result["K1"] == pytest.approx(ts1)
    assert result["K2"] == pytest.approx(ts2)


def test_list_expiries_empty_project(expiry_dir):
    assert list_expiries("empty_proj", base_dir=expiry_dir) == {}


def test_set_expiry_overwrites_existing(expiry_dir):
    set_expiry("myapp", "KEY", time.time() + 100, base_dir=expiry_dir)
    new_ts = time.time() + 9999
    set_expiry("myapp", "KEY", new_ts, base_dir=expiry_dir)
    assert get_expiry("myapp", "KEY", base_dir=expiry_dir) == pytest.approx(new_ts)
