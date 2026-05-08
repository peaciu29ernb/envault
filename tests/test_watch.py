"""Tests for envault.watch module."""

import time
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call

from envault.watch import _get_mtime, watch_env_file, build_reencrypt_callback


# ---------------------------------------------------------------------------
# _get_mtime
# ---------------------------------------------------------------------------

def test_get_mtime_existing_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value")
    mtime = _get_mtime(str(f))
    assert isinstance(mtime, float)
    assert mtime > 0


def test_get_mtime_missing_file(tmp_path):
    result = _get_mtime(str(tmp_path / "nonexistent.env"))
    assert result is None


# ---------------------------------------------------------------------------
# watch_env_file
# ---------------------------------------------------------------------------

def test_watch_calls_on_change_when_file_modified(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=1")

    callback = MagicMock()
    mtimes = iter([1000.0, 1000.0, 1001.0])  # change on third poll

    with patch("envault.watch._get_mtime", side_effect=mtimes), \
         patch("time.sleep"):
        watch_env_file(str(env_file), callback, interval=0, max_iterations=3)

    callback.assert_called_once_with(str(env_file))


def test_watch_no_change_does_not_call_callback(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=1")

    callback = MagicMock()
    mtimes = iter([1000.0, 1000.0, 1000.0])

    with patch("envault.watch._get_mtime", side_effect=mtimes), \
         patch("time.sleep"):
        watch_env_file(str(env_file), callback, interval=0, max_iterations=3)

    callback.assert_not_called()


def test_watch_respects_max_iterations(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=1")

    sleep_mock = MagicMock()
    # always return same mtime so no callback fires; we just count iterations
    with patch("envault.watch._get_mtime", return_value=999.0), \
         patch("time.sleep", sleep_mock):
        watch_env_file(str(env_file), MagicMock(), interval=0.5, max_iterations=4)

    assert sleep_mock.call_count == 4


def test_watch_handles_missing_file_gracefully(tmp_path):
    """Watcher should not crash when the file doesn't exist yet."""
    callback = MagicMock()
    mtimes = iter([None, None, None])

    with patch("envault.watch._get_mtime", side_effect=mtimes), \
         patch("time.sleep"):
        watch_env_file("ghost.env", callback, interval=0, max_iterations=3)

    callback.assert_not_called()


# ---------------------------------------------------------------------------
# build_reencrypt_callback
# ---------------------------------------------------------------------------

def test_build_reencrypt_callback_stores_new_key(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("SECRET=abc")
    vault_path = str(tmp_path / "vault.env.enc")

    with patch("envault.watch.retrieve_key", side_effect=KeyError("no key")), \
         patch("envault.watch.create_vault", return_value=({"data": "x"}, b"newkey")), \
         patch("envault.watch.save_vault") as mock_save, \
         patch("envault.watch.store_key") as mock_store, \
         patch("envault.watch.record_event") as mock_audit:

        cb = build_reencrypt_callback(vault_path, "myproject")
        cb(str(env_file))

    mock_store.assert_called_once_with("myproject", b"newkey")
    mock_save.assert_called_once()
    mock_audit.assert_called_once()


def test_build_reencrypt_callback_reuses_existing_key(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("TOKEN=xyz")
    vault_path = str(tmp_path / "vault.env.enc")
    existing_key = b"existingkey"

    with patch("envault.watch.retrieve_key", return_value=existing_key), \
         patch("envault.watch.create_vault", return_value=({"data": "y"}, existing_key)) as mock_cv, \
         patch("envault.watch.save_vault"), \
         patch("envault.watch.store_key") as mock_store, \
         patch("envault.watch.record_event"):

        cb = build_reencrypt_callback(vault_path, "proj2")
        cb(str(env_file))

    mock_cv.assert_called_once_with(
        env_path=str(env_file), key=existing_key, password=None
    )
    mock_store.assert_not_called()
