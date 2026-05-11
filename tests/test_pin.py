"""Tests for envault.pin module."""

from __future__ import annotations

import pytest
from pathlib import Path
from envault.pin import pin_key, unpin_key, get_pins, is_pinned, clear_pins


@pytest.fixture
def pin_dir(tmp_path: Path) -> Path:
    return tmp_path / "pins"


def test_pin_key_adds_key(pin_dir):
    result = pin_key("myproject", "SECRET_KEY", base_dir=pin_dir)
    assert "SECRET_KEY" in result


def test_pin_key_no_duplicates(pin_dir):
    pin_key("myproject", "SECRET_KEY", base_dir=pin_dir)
    result = pin_key("myproject", "SECRET_KEY", base_dir=pin_dir)
    assert result.count("SECRET_KEY") == 1


def test_pin_multiple_keys(pin_dir):
    pin_key("myproject", "KEY_A", base_dir=pin_dir)
    result = pin_key("myproject", "KEY_B", base_dir=pin_dir)
    assert "KEY_A" in result
    assert "KEY_B" in result


def test_get_pins_empty_when_none(pin_dir):
    assert get_pins("newproject", base_dir=pin_dir) == []


def test_get_pins_returns_sorted(pin_dir):
    pin_key("myproject", "ZEBRA", base_dir=pin_dir)
    pin_key("myproject", "ALPHA", base_dir=pin_dir)
    pins = get_pins("myproject", base_dir=pin_dir)
    assert pins == sorted(pins)


def test_is_pinned_true(pin_dir):
    pin_key("myproject", "DB_PASSWORD", base_dir=pin_dir)
    assert is_pinned("myproject", "DB_PASSWORD", base_dir=pin_dir) is True


def test_is_pinned_false(pin_dir):
    assert is_pinned("myproject", "NONEXISTENT", base_dir=pin_dir) is False


def test_unpin_key_returns_true(pin_dir):
    pin_key("myproject", "TOKEN", base_dir=pin_dir)
    assert unpin_key("myproject", "TOKEN", base_dir=pin_dir) is True
    assert is_pinned("myproject", "TOKEN", base_dir=pin_dir) is False


def test_unpin_key_returns_false_when_not_pinned(pin_dir):
    assert unpin_key("myproject", "MISSING", base_dir=pin_dir) is False


def test_clear_pins_returns_count(pin_dir):
    pin_key("myproject", "A", base_dir=pin_dir)
    pin_key("myproject", "B", base_dir=pin_dir)
    count = clear_pins("myproject", base_dir=pin_dir)
    assert count == 2
    assert get_pins("myproject", base_dir=pin_dir) == []


def test_clear_pins_no_file_returns_zero(pin_dir):
    count = clear_pins("ghost", base_dir=pin_dir)
    assert count == 0


def test_pins_isolated_per_project(pin_dir):
    pin_key("proj_a", "KEY", base_dir=pin_dir)
    assert is_pinned("proj_b", "KEY", base_dir=pin_dir) is False
