import pytest
from envault.placeholder import (
    is_placeholder,
    find_placeholders,
    placeholder_keys,
    has_placeholders,
    placeholder_report,
)


# ---------------------------------------------------------------------------
# is_placeholder
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value", [
    "<MY_SECRET>",
    "{{DATABASE_URL}}",
    "${API_KEY}",
    "%SOME_VALUE%",
    "CHANGEME",
    "changeme",
    "TODO",
    "todo",
    "REPLACE_ME",
    "replace_me",
    "YOUR_API_KEY",
    "FILL_IN",
    "FILLIN",
    "<REQUIRED>",
    "PLACEHOLDER",
])
def test_is_placeholder_true(value):
    assert is_placeholder(value) is True


@pytest.mark.parametrize("value", [
    "https://example.com",
    "my_actual_password_123",
    "",
    "localhost",
    "5432",
    "true",
    "some_token_abc123",
])
def test_is_placeholder_false(value):
    assert is_placeholder(value) is False


def test_is_placeholder_strips_surrounding_whitespace():
    assert is_placeholder("  <MY_VAR>  ") is True


# ---------------------------------------------------------------------------
# find_placeholders
# ---------------------------------------------------------------------------

def test_find_placeholders_returns_matching_keys():
    env = {"DB_URL": "<DB_URL>", "PORT": "5432", "KEY": "{{KEY}}"}
    result = find_placeholders(env)
    assert result == {"DB_URL": "<DB_URL>", "KEY": "{{KEY}}"}


def test_find_placeholders_empty_env():
    assert find_placeholders({}) == {}


def test_find_placeholders_no_matches():
    env = {"HOST": "localhost", "PORT": "3000"}
    assert find_placeholders(env) == {}


# ---------------------------------------------------------------------------
# placeholder_keys
# ---------------------------------------------------------------------------

def test_placeholder_keys_sorted():
    env = {"Z_KEY": "CHANGEME", "A_KEY": "<A_KEY>", "M_KEY": "real_value"}
    assert placeholder_keys(env) == ["A_KEY", "Z_KEY"]


# ---------------------------------------------------------------------------
# has_placeholders
# ---------------------------------------------------------------------------

def test_has_placeholders_true():
    assert has_placeholders({"SECRET": "TODO", "HOST": "localhost"}) is True


def test_has_placeholders_false():
    assert has_placeholders({"HOST": "localhost", "PORT": "8080"}) is False


def test_has_placeholders_empty():
    assert has_placeholders({}) is False


# ---------------------------------------------------------------------------
# placeholder_report
# ---------------------------------------------------------------------------

def test_placeholder_report_no_placeholders():
    assert placeholder_report({"HOST": "localhost"}) == "No placeholders found."


def test_placeholder_report_lists_keys():
    env = {"API_KEY": "<API_KEY>", "HOST": "localhost"}
    report = placeholder_report(env)
    assert "Placeholder values detected:" in report
    assert "API_KEY=<API_KEY>" in report
    assert "HOST" not in report
