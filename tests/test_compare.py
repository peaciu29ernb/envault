"""Tests for envault.compare module."""

import json
import os
import pytest

from envault.compare import (
    CompareReport,
    compare_dicts,
    compare_vaults,
    format_compare_report,
)
from envault.vault import create_vault, save_vault


# ---------------------------------------------------------------------------
# compare_dicts
# ---------------------------------------------------------------------------

def test_compare_dicts_identical():
    a = {"FOO": "bar", "BAZ": "qux"}
    report = compare_dicts(a, a.copy())
    assert not report.has_differences
    assert sorted(report.unchanged) == ["BAZ", "FOO"]


def test_compare_dicts_only_in_a():
    a = {"FOO": "1", "EXTRA": "x"}
    b = {"FOO": "1"}
    report = compare_dicts(a, b)
    assert report.only_in_a == ["EXTRA"]
    assert report.only_in_b == []
    assert report.has_differences


def test_compare_dicts_only_in_b():
    a = {"FOO": "1"}
    b = {"FOO": "1", "NEW": "val"}
    report = compare_dicts(a, b)
    assert report.only_in_b == ["NEW"]
    assert report.only_in_a == []


def test_compare_dicts_changed_values():
    a = {"KEY": "old"}
    b = {"KEY": "new"}
    report = compare_dicts(a, b)
    assert "KEY" in report.changed
    assert report.changed["KEY"] == ("old", "new")


def test_compare_dicts_mixed():
    a = {"A": "1", "B": "2", "C": "same"}
    b = {"B": "changed", "C": "same", "D": "new"}
    report = compare_dicts(a, b)
    assert report.only_in_a == ["A"]
    assert report.only_in_b == ["D"]
    assert "B" in report.changed
    assert report.unchanged == ["C"]


# ---------------------------------------------------------------------------
# to_dict
# ---------------------------------------------------------------------------

def test_to_dict_structure():
    report = compare_dicts({"X": "1", "Y": "old"}, {"Y": "new", "Z": "3"})
    d = report.to_dict()
    assert d["only_in_a"] == ["X"]
    assert d["only_in_b"] == ["Z"]
    assert d["changed"]["Y"] == {"a": "old", "b": "new"}


# ---------------------------------------------------------------------------
# format_compare_report
# ---------------------------------------------------------------------------

def test_format_no_differences():
    report = compare_dicts({"K": "v"}, {"K": "v"})
    out = format_compare_report(report)
    assert "No differences" in out


def test_format_shows_only_in_a():
    report = compare_dicts({"GONE": "x"}, {})
    out = format_compare_report(report)
    assert "GONE" in out and "only in A" in out


def test_format_shows_changed():
    report = compare_dicts({"K": "old"}, {"K": "new"})
    out = format_compare_report(report)
    assert "~ K" in out
    assert "A: old" in out
    assert "B: new" in out


def test_format_show_unchanged_flag():
    report = compare_dicts({"SAME": "v"}, {"SAME": "v"})
    out = format_compare_report(report, show_unchanged=True)
    assert "SAME" in out and "unchanged" in out


# ---------------------------------------------------------------------------
# compare_vaults (integration)
# ---------------------------------------------------------------------------

def test_compare_vaults_roundtrip(tmp_path):
    env_a = {"DB": "postgres", "PORT": "5432"}
    env_b = {"DB": "mysql", "PORT": "5432", "HOST": "localhost"}

    vault_a = str(tmp_path / "a.vault")
    vault_b = str(tmp_path / "b.vault")

    data_a, key_a = create_vault(env_a)
    save_vault(vault_a, data_a)

    data_b, key_b = create_vault(env_b)
    save_vault(vault_b, data_b)

    report = compare_vaults(vault_a, vault_b, key_a=key_a, key_b=key_b)
    assert "HOST" in report.only_in_b
    assert "DB" in report.changed
    assert report.changed["DB"] == ("postgres", "mysql")
    assert "PORT" in report.unchanged
