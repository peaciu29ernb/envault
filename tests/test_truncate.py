import pytest
from envault.truncate import (
    TruncateError,
    truncate_value,
    truncate_env,
    truncate_report,
)


# ---------------------------------------------------------------------------
# truncate_value
# ---------------------------------------------------------------------------

def test_truncate_value_short_value_unchanged():
    assert truncate_value("hello", 10) == "hello"


def test_truncate_value_exact_length_unchanged():
    assert truncate_value("hello", 5) == "hello"


def test_truncate_value_appends_suffix():
    result = truncate_value("hello world", 8)
    assert result == "hello..."
    assert len(result) == 8


def test_truncate_value_custom_suffix():
    result = truncate_value("abcdefgh", 5, suffix="--")
    assert result == "abc--"


def test_truncate_value_no_suffix():
    result = truncate_value("abcdefgh", 5, suffix="")
    assert result == "abcde"


def test_truncate_value_negative_max_length_raises():
    with pytest.raises(TruncateError, match="max_length must be >= 0"):
        truncate_value("hello", -1)


def test_truncate_value_suffix_longer_than_max_strict_raises():
    with pytest.raises(TruncateError, match="too short"):
        truncate_value("hello world", 2, suffix="...", strict=True)


def test_truncate_value_suffix_longer_than_max_non_strict_slices():
    result = truncate_value("hello world", 2, suffix="...", strict=False)
    assert result == "he"


def test_truncate_value_zero_max_length_returns_empty():
    result = truncate_value("hello", 0, suffix="")
    assert result == ""


# ---------------------------------------------------------------------------
# truncate_env
# ---------------------------------------------------------------------------

def test_truncate_env_truncates_all_values():
    env = {"A": "short", "B": "this is a long value"}
    result = truncate_env(env, 8)
    assert result["A"] == "short"
    assert result["B"] == "this ..."  # 5 chars + "..."


def test_truncate_env_does_not_mutate_original():
    env = {"K": "a" * 20}
    truncate_env(env, 5)
    assert env["K"] == "a" * 20


def test_truncate_env_selective_keys():
    env = {"A": "longvalue", "B": "longvalue"}
    result = truncate_env(env, 6, keys=["A"])
    assert result["A"] == "lon..."
    assert result["B"] == "longvalue"  # untouched


def test_truncate_env_empty_env():
    assert truncate_env({}, 10) == {}


def test_truncate_env_all_short_values_unchanged():
    env = {"X": "hi", "Y": "bye"}
    result = truncate_env(env, 100)
    assert result == env


# ---------------------------------------------------------------------------
# truncate_report
# ---------------------------------------------------------------------------

def test_truncate_report_identifies_long_values():
    env = {"A": "short", "B": "this is definitely too long"}
    report = truncate_report(env, 10)
    assert len(report) == 1
    assert report[0]["key"] == "B"
    assert report[0]["original_length"] == len("this is definitely too long")
    assert report[0]["truncated_length"] == 10


def test_truncate_report_empty_when_all_fit():
    env = {"A": "ok", "B": "fine"}
    assert truncate_report(env, 50) == []


def test_truncate_report_multiple_long_values():
    env = {"A": "x" * 20, "B": "y" * 30, "C": "z"}
    report = truncate_report(env, 10)
    keys_in_report = {r["key"] for r in report}
    assert keys_in_report == {"A", "B"}
