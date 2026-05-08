"""Tests for envault/export.py"""

import json
import pytest
from envault.export import (
    export_as_env,
    export_as_json,
    export_as_shell,
    export_as_docker,
    export_env,
    SUPPORTED_FORMATS,
)


SAMPLE = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "s3cr3t"}
SPECIAL = {"MSG": "hello world", "QUOTE": 'say "hi"', "APOS": "it's fine"}


def test_export_as_env_basic():
    result = export_as_env(SAMPLE)
    assert "DB_HOST=localhost" in result
    assert "DB_PORT=5432" in result
    assert "SECRET=s3cr3t" in result


def test_export_as_env_quotes_values_with_spaces():
    result = export_as_env({"MSG": "hello world"})
    assert 'MSG="hello world"' in result


def test_export_as_env_quotes_values_with_double_quotes():
    result = export_as_env({"VAL": 'say "hi"'})
    assert 'VAL=' in result
    assert '\\"' in result


def test_export_as_env_empty():
    assert export_as_env({}) == ""


def test_export_as_json_valid():
    result = export_as_json(SAMPLE)
    parsed = json.loads(result)
    assert parsed == SAMPLE


def test_export_as_json_indent():
    result = export_as_json({"A": "1"}, indent=4)
    assert "    " in result


def test_export_as_shell_basic():
    result = export_as_shell(SAMPLE)
    assert "export DB_HOST='localhost'" in result
    assert "export DB_PORT='5432'" in result


def test_export_as_shell_escapes_single_quotes():
    result = export_as_shell({"VAL": "it's fine"})
    assert "export VAL=" in result
    # Single quotes inside are escaped
    assert "'\"'\"'" in result


def test_export_as_docker_basic():
    result = export_as_docker(SAMPLE)
    assert "DB_HOST=localhost" in result
    assert "DB_PORT=5432" in result


def test_export_env_dispatches_correctly():
    assert export_env(SAMPLE, "env") == export_as_env(SAMPLE)
    assert export_env(SAMPLE, "json") == export_as_json(SAMPLE)
    assert export_env(SAMPLE, "shell") == export_as_shell(SAMPLE)
    assert export_env(SAMPLE, "docker") == export_as_docker(SAMPLE)


def test_export_env_invalid_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_env(SAMPLE, "xml")


def test_supported_formats_constant():
    assert "env" in SUPPORTED_FORMATS
    assert "json" in SUPPORTED_FORMATS
    assert "shell" in SUPPORTED_FORMATS
    assert "docker" in SUPPORTED_FORMATS
