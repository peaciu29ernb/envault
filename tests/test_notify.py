"""Tests for envault.notify and envault.cli_notify."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.notify import (
    add_channel,
    fire,
    list_channels,
    register_hook,
    remove_channel,
    unregister_hooks,
)
from envault.cli_notify import notify_cmd


# ---------------------------------------------------------------------------
# Unit tests for envault.notify
# ---------------------------------------------------------------------------


def test_add_channel_stores_channel(tmp_path):
    add_channel("slack", base_dir=str(tmp_path))
    assert "slack" in list_channels(base_dir=str(tmp_path))


def test_add_channel_no_duplicates(tmp_path):
    add_channel("email", base_dir=str(tmp_path))
    add_channel("email", base_dir=str(tmp_path))
    assert list_channels(base_dir=str(tmp_path)).count("email") == 1


def test_list_channels_empty_when_none(tmp_path):
    assert list_channels(base_dir=str(tmp_path)) == []


def test_remove_channel_returns_true(tmp_path):
    add_channel("teams", base_dir=str(tmp_path))
    result = remove_channel("teams", base_dir=str(tmp_path))
    assert result is True
    assert "teams" not in list_channels(base_dir=str(tmp_path))


def test_remove_missing_channel_returns_false(tmp_path):
    assert remove_channel("nonexistent", base_dir=str(tmp_path)) is False


def test_fire_calls_registered_hook():
    received = []
    register_hook("test_event", lambda p: received.append(p))
    try:
        outcomes = fire("test_event", {"key": "value"})
        assert outcomes == ["ok"]
        assert received == [{"key": "value"}]
    finally:
        unregister_hooks("test_event")


def test_fire_no_hooks_returns_empty():
    outcomes = fire("unregistered_event", {})
    assert outcomes == []


def test_fire_hook_exception_captured():
    def bad_hook(payload):
        raise RuntimeError("boom")

    register_hook("fail_event", bad_hook)
    try:
        outcomes = fire("fail_event", {})
        assert len(outcomes) == 1
        assert "error" in outcomes[0]
    finally:
        unregister_hooks("fail_event")


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_notify_add(runner, tmp_path):
    result = runner.invoke(notify_cmd, ["add", "slack", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "slack" in result.output


def test_cli_notify_list(runner, tmp_path):
    add_channel("pagerduty", base_dir=str(tmp_path))
    result = runner.invoke(notify_cmd, ["list", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "pagerduty" in result.output


def test_cli_notify_remove(runner, tmp_path):
    add_channel("webhook", base_dir=str(tmp_path))
    result = runner.invoke(notify_cmd, ["remove", "webhook", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cli_notify_remove_missing(runner, tmp_path):
    result = runner.invoke(notify_cmd, ["remove", "ghost", "--base-dir", str(tmp_path)])
    assert result.exit_code != 0


def test_cli_notify_fire_no_hooks(runner):
    result = runner.invoke(notify_cmd, ["fire", "rotation", "--project", "myapp"])
    assert result.exit_code == 0
    assert "no hooks" in result.output
