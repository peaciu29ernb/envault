"""Tests for envault.template module."""

import os
import pytest

from envault.template import (
    MissingVariableError,
    list_placeholders,
    render_file,
    render_template,
)


# ---------------------------------------------------------------------------
# render_template
# ---------------------------------------------------------------------------

def test_render_template_braced():
    result = render_template("Hello, ${NAME}!", {"NAME": "World"})
    assert result == "Hello, World!"


def test_render_template_unbraced():
    result = render_template("Hello, $NAME!", {"NAME": "Alice"})
    assert result == "Hello, Alice!"


def test_render_template_mixed_styles():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = render_template("${HOST}:$PORT", env)
    assert result == "localhost:5432"


def test_render_template_multiple_occurrences():
    result = render_template("$A + $A = two", {"A": "one"})
    assert result == "one + one = two"


def test_render_template_strict_raises_on_missing():
    with pytest.raises(MissingVariableError, match="MISSING"):
        render_template("value=${MISSING}", {}, strict=True)


def test_render_template_non_strict_leaves_placeholder():
    result = render_template("value=${MISSING}", {}, strict=False)
    assert result == "value=${MISSING}"


def test_render_template_empty_template():
    assert render_template("", {"A": "1"}) == ""


def test_render_template_no_placeholders():
    assert render_template("plain text", {"A": "1"}) == "plain text"


# ---------------------------------------------------------------------------
# list_placeholders
# ---------------------------------------------------------------------------

def test_list_placeholders_basic():
    placeholders = list_placeholders("${DB_HOST}:${DB_PORT}")
    assert placeholders == ["DB_HOST", "DB_PORT"]


def test_list_placeholders_deduplicates():
    placeholders = list_placeholders("$A and $A again")
    assert placeholders == ["A"]


def test_list_placeholders_empty():
    assert list_placeholders("no vars here") == []


# ---------------------------------------------------------------------------
# render_file
# ---------------------------------------------------------------------------

def test_render_file_reads_and_renders(tmp_path):
    tpl = tmp_path / "config.tpl"
    tpl.write_text("DB=${DB_URL}\nDEBUG=$DEBUG\n")
    env = {"DB_URL": "postgres://localhost/mydb", "DEBUG": "false"}
    result = render_file(str(tpl), env)
    assert result == "DB=postgres://localhost/mydb\nDEBUG=false\n"


def test_render_file_writes_output(tmp_path):
    tpl = tmp_path / "nginx.conf.tpl"
    tpl.write_text("server_name ${DOMAIN};\n")
    out = tmp_path / "nginx.conf"
    render_file(str(tpl), {"DOMAIN": "example.com"}, output_path=str(out))
    assert out.read_text() == "server_name example.com;\n"


def test_render_file_strict_missing_raises(tmp_path):
    tpl = tmp_path / "bad.tpl"
    tpl.write_text("value=${NOPE}")
    with pytest.raises(MissingVariableError):
        render_file(str(tpl), {})
