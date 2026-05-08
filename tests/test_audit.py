"""Tests for envault.audit module."""

import json
from pathlib import Path

import pytest

from envault.audit import record_event, read_events, clear_events


@pytest.fixture
def log_file(tmp_path):
    return tmp_path / "audit.log"


def test_record_event_creates_file(log_file):
    record_event("init", "myproject", log_path=log_file)
    assert log_file.exists()


def test_record_event_returns_dict(log_file):
    event = record_event("init", "myproject", details="created", log_path=log_file)
    assert event["action"] == "init"
    assert event["project"] == "myproject"
    assert event["details"] == "created"
    assert "timestamp" in event


def test_record_event_appends(log_file):
    record_event("init", "proj", log_path=log_file)
    record_event("rotate", "proj", log_path=log_file)
    events = read_events(log_path=log_file)
    assert len(events) == 2
    assert events[0]["action"] == "init"
    assert events[1]["action"] == "rotate"


def test_read_events_empty_when_no_file(tmp_path):
    missing = tmp_path / "nonexistent.log"
    events = read_events(log_path=missing)
    assert events == []


def test_read_events_filter_by_project(log_file):
    record_event("init", "alpha", log_path=log_file)
    record_event("decrypt", "beta", log_path=log_file)
    record_event("rotate", "alpha", log_path=log_file)

    alpha_events = read_events(project="alpha", log_path=log_file)
    assert len(alpha_events) == 2
    assert all(e["project"] == "alpha" for e in alpha_events)


def test_read_events_no_filter_returns_all(log_file):
    record_event("init", "alpha", log_path=log_file)
    record_event("init", "beta", log_path=log_file)
    events = read_events(log_path=log_file)
    assert len(events) == 2


def test_clear_events_returns_count(log_file):
    record_event("init", "proj", log_path=log_file)
    record_event("rotate", "proj", log_path=log_file)
    count = clear_events(log_path=log_file)
    assert count == 2


def test_clear_events_empties_log(log_file):
    record_event("init", "proj", log_path=log_file)
    clear_events(log_path=log_file)
    events = read_events(log_path=log_file)
    assert events == []


def test_clear_events_no_file_returns_zero(tmp_path):
    missing = tmp_path / "no.log"
    assert clear_events(log_path=missing) == 0


def test_event_timestamp_is_utc_iso(log_file):
    event = record_event("init", "proj", log_path=log_file)
    ts = event["timestamp"]
    assert ts.endswith("+00:00") or ts.endswith("Z")
