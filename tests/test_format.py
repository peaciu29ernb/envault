"""Tests for envault.format conversion utilities."""

import json
import pytest
from envault.format import (
    from_env_string,
    to_env_string,
    from_json_string,
    to_json_string,
    from_ini_string,
    to_ini_string,
    FormatError,
)


# --- from_env_string ---

def test_from_env_basic():
    text = "FOO=bar\nBAZ=qux\n"
    assert from_env_string(text) == {"FOO": "bar", "BAZ": "qux"}


def test_from_env_skips_comments_and_blanks():
    text = "# comment\n\nKEY=value\n"
    assert from_env_string(text) == {"KEY": "value"}


def test_from_env_strips_double_quotes():
    assert from_env_string('KEY="hello world"') == {"KEY": "hello world"}


def test_from_env_strips_single_quotes():
    assert from_env_string("KEY='hello'") == {"KEY": "hello"}


def test_from_env_missing_equals_raises():
    with pytest.raises(FormatError, match="missing '='"):
        from_env_string("BADLINE")


def test_from_env_empty_key_raises():
    with pytest.raises(FormatError, match="empty key"):
        from_env_string("=value")


# --- to_env_string ---

def test_to_env_basic():
    result = to_env_string({"A": "1", "B": "2"})
    lines = result.strip().splitlines()
    assert "A=1" in lines
    assert "B=2" in lines


def test_to_env_quotes_values_with_spaces():
    result = to_env_string({"MSG": "hello world"})
    assert 'MSG="hello world"' in result


def test_to_env_quotes_empty_values():
    result = to_env_string({"EMPTY": ""})
    assert 'EMPTY=""' in result


def test_to_env_roundtrip():
    original = {"HOST": "localhost", "PORT": "5432", "DB": "mydb"}
    assert from_env_string(to_env_string(original)) == original


# --- from_json_string ---

def test_from_json_basic():
    text = json.dumps({"X": "1", "Y": "2"})
    assert from_json_string(text) == {"X": "1", "Y": "2"}


def test_from_json_invalid_raises():
    with pytest.raises(FormatError, match="Invalid JSON"):
        from_json_string("{not valid")


def test_from_json_non_object_raises():
    with pytest.raises(FormatError, match="root must be an object"):
        from_json_string("[1, 2, 3]")


# --- to_json_string ---

def test_to_json_valid_json():
    result = to_json_string({"K": "V"})
    parsed = json.loads(result)
    assert parsed == {"K": "V"}


def test_to_json_roundtrip():
    original = {"A": "alpha", "B": "beta"}
    assert from_json_string(to_json_string(original)) == original


# --- from_ini_string / to_ini_string ---

def test_to_ini_and_from_ini_roundtrip():
    original = {"HOST": "localhost", "PORT": "3306"}
    ini_text = to_ini_string(original)
    assert from_ini_string(ini_text) == original


def test_from_ini_missing_section_raises():
    with pytest.raises(FormatError, match="section"):
        from_ini_string("[other]\nkey=val", section="env")


def test_to_ini_custom_section():
    text = to_ini_string({"K": "V"}, section="vars")
    assert from_ini_string(text, section="vars") == {"K": "V"}
