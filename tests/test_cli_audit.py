"""Tests for the audit CLI commands."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_audit import audit_cmd
from envault.audit import record_event


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def log_file(tmp_path):
    return tmp_path / "audit.log"


def test_show_no_events(runner, log_file):
    result = runner.invoke(audit_cmd, ["show", "--log", str(log_file)])
    assert result.exit_code == 0
    assert "No audit events found" in result.output


def test_show_events(runner, log_file):
    record_event("init", "myproject", details="created", log_path=log_file)
    result = runner.invoke(audit_cmd, ["show", "--log", str(log_file)])
    assert result.exit_code == 0
    assert "init" in result.output
    assert "myproject" in result.output
    assert "created" in result.output


def test_show_filter_by_project(runner, log_file):
    record_event("init", "alpha", log_path=log_file)
    record_event("rotate", "beta", log_path=log_file)
    result = runner.invoke(
        audit_cmd, ["show", "--project", "alpha", "--log", str(log_file)]
    )
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" not in result.output


def test_clear_audit_confirmed(runner, log_file):
    record_event("init", "proj", log_path=log_file)
    record_event("rotate", "proj", log_path=log_file)
    result = runner.invoke(
        audit_cmd, ["clear", "--log", str(log_file)], input="y\n"
    )
    assert result.exit_code == 0
    assert "Cleared 2" in result.output


def test_clear_audit_aborted(runner, log_file):
    record_event("init", "proj", log_path=log_file)
    result = runner.invoke(
        audit_cmd, ["clear", "--log", str(log_file)], input="n\n"
    )
    assert result.exit_code != 0 or "Aborted" in result.output
    # event should still be present
    from envault.audit import read_events
    events = read_events(log_path=log_file)
    assert len(events) == 1


def test_show_multiple_events_ordering(runner, log_file):
    record_event("init", "proj", log_path=log_file)
    record_event("decrypt", "proj", log_path=log_file)
    record_event("rotate", "proj", log_path=log_file)
    result = runner.invoke(audit_cmd, ["show", "--log", str(log_file)])
    assert result.exit_code == 0
    lines = [l for l in result.output.splitlines() if l.strip()]
    assert len(lines) == 3
    assert "init" in lines[0]
    assert "rotate" in lines[2]
