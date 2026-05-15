"""Tests for envault.mask module."""

import pytest
from envault.mask import (
    mask_value,
    mask_env,
    format_masked_env,
)


def test_mask_value_hides_most_of_value():
    result = mask_value("supersecret")
    assert result == "supe****"


def test_mask_value_short_value_fully_masked():
    result = mask_value("abc", visible_chars=4)
    assert result == "****"


def test_mask_value_empty_string():
    assert mask_value("") == "****"


def test_mask_value_custom_mask():
    result = mask_value("mypassword", mask="[REDACTED]")
    assert result == "mypa[REDACTED]"


def test_mask_value_show_suffix():
    result = mask_value("supersecret", visible_chars=4, show_suffix=True)
    assert result == "****cret"


def test_mask_value_zero_visible_chars():
    result = mask_value("hello", visible_chars=0)
    assert result == "****"


def test_mask_env_masks_all_keys_by_default():
    env = {"API_KEY": "abc123", "HOST": "localhost"}
    masked = mask_env(env)
    assert masked["API_KEY"] == "abc1****"
    assert masked["HOST"] == "loca****"


def test_mask_env_masks_only_specified_keys():
    env = {"API_KEY": "abc12345", "HOST": "localhost"}
    masked = mask_env(env, keys=["API_KEY"])
    assert masked["API_KEY"] == "abc1****"
    assert masked["HOST"] == "localhost"


def test_mask_env_returns_copy_not_original():
    env = {"SECRET": "topsecret"}
    masked = mask_env(env)
    assert env["SECRET"] == "topsecret"
    assert masked["SECRET"] != "topsecret"


def test_mask_env_empty_dict():
    assert mask_env({}) == {}


def test_format_masked_env_returns_sorted_lines():
    env = {"Z_KEY": "zvalue123", "A_KEY": "avalue456"}
    output = format_masked_env(env)
    lines = output.splitlines()
    assert lines[0].startswith("A_KEY=")
    assert lines[1].startswith("Z_KEY=")


def test_format_masked_env_only_masks_specified_keys():
    env = {"TOKEN": "abc12345", "NAME": "alice"}
    output = format_masked_env(env, keys=["TOKEN"])
    assert "abc1****" in output
    assert "alice" in output


def test_format_masked_env_empty():
    assert format_masked_env({}) == ""
