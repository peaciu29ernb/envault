"""Tests for envault.lock and envault.cli_lock."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.lock import (
    lock_key,
    unlock_key,
    get_locks,
    is_locked,
    assert_not_locked,
    clear_locks,
)
from envault.cli_lock import lock_cmd


@pytest.fixture
def lock_dir(tmp_path):
    return tmp_path / "locks"


# --- Unit tests ---

def test_lock_key_adds_key(lock_dir):
    result = lock_key("proj", "SECRET_KEY", base_dir=lock_dir)
    assert "SECRET_KEY" in result


def test_lock_key_no_duplicates(lock_dir):
    lock_key("proj", "SECRET_KEY", base_dir=lock_dir)
    result = lock_key("proj", "SECRET_KEY", base_dir=lock_dir)
    assert result.count("SECRET_KEY") == 1


def test_lock_multiple_keys(lock_dir):
    lock_key("proj", "KEY_A", base_dir=lock_dir)
    lock_key("proj", "KEY_B", base_dir=lock_dir)
    locks = get_locks("proj", base_dir=lock_dir)
    assert "KEY_A" in locks
    assert "KEY_B" in locks


def test_get_locks_empty_when_none(lock_dir):
    assert get_locks("proj", base_dir=lock_dir) == []


def test_is_locked_true(lock_dir):
    lock_key("proj", "DB_PASS", base_dir=lock_dir)
    assert is_locked("proj", "DB_PASS", base_dir=lock_dir) is True


def test_is_locked_false(lock_dir):
    assert is_locked("proj", "NOT_LOCKED", base_dir=lock_dir) is False


def test_unlock_key_returns_true(lock_dir):
    lock_key("proj", "API_KEY", base_dir=lock_dir)
    result = unlock_key("proj", "API_KEY", base_dir=lock_dir)
    assert result is True
    assert is_locked("proj", "API_KEY", base_dir=lock_dir) is False


def test_unlock_missing_key_returns_false(lock_dir):
    result = unlock_key("proj", "GHOST", base_dir=lock_dir)
    assert result is False


def test_assert_not_locked_raises(lock_dir):
    lock_key("proj", "SECRET", base_dir=lock_dir)
    with pytest.raises(ValueError, match="locked"):
        assert_not_locked("proj", "SECRET", base_dir=lock_dir)


def test_assert_not_locked_passes(lock_dir):
    assert_not_locked("proj", "FREE_KEY", base_dir=lock_dir)  # should not raise


def test_clear_locks_removes_all(lock_dir):
    lock_key("proj", "A", base_dir=lock_dir)
    lock_key("proj", "B", base_dir=lock_dir)
    clear_locks("proj", base_dir=lock_dir)
    assert get_locks("proj", base_dir=lock_dir) == []


# --- CLI tests ---

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_lock_add(runner, lock_dir):
    result = runner.invoke(lock_cmd, ["add", "proj", "MY_KEY", "--base-dir", str(lock_dir)])
    assert result.exit_code == 0
    assert "Locked 'MY_KEY'" in result.output


def test_cli_lock_list(runner, lock_dir):
    lock_key("proj", "MY_KEY", base_dir=lock_dir)
    result = runner.invoke(lock_cmd, ["list", "proj", "--base-dir", str(lock_dir)])
    assert result.exit_code == 0
    assert "MY_KEY" in result.output


def test_cli_lock_remove(runner, lock_dir):
    lock_key("proj", "MY_KEY", base_dir=lock_dir)
    result = runner.invoke(lock_cmd, ["remove", "proj", "MY_KEY", "--base-dir", str(lock_dir)])
    assert result.exit_code == 0
    assert "Unlocked" in result.output


def test_cli_lock_check_locked(runner, lock_dir):
    lock_key("proj", "MY_KEY", base_dir=lock_dir)
    result = runner.invoke(lock_cmd, ["check", "proj", "MY_KEY", "--base-dir", str(lock_dir)])
    assert result.exit_code == 0
    assert "LOCKED" in result.output


def test_cli_lock_check_unlocked(runner, lock_dir):
    result = runner.invoke(lock_cmd, ["check", "proj", "FREE", "--base-dir", str(lock_dir)])
    assert result.exit_code == 0
    assert "unlocked" in result.output
