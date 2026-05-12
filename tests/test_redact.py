"""Tests for envault.redact module."""

import pytest
from envault.redact import (
    REDACT_PLACEHOLDER,
    is_sensitive_key,
    redact_value,
    redact_env,
    list_sensitive_keys,
)


# ---------------------------------------------------------------------------
# is_sensitive_key
# ---------------------------------------------------------------------------

def test_is_sensitive_key_matches_password():
    assert is_sensitive_key("DB_PASSWORD") is True


def test_is_sensitive_key_matches_api_key():
    assert is_sensitive_key("STRIPE_API_KEY") is True


def test_is_sensitive_key_matches_token():
    assert is_sensitive_key("ACCESS_TOKEN") is True


def test_is_sensitive_key_non_sensitive():
    assert is_sensitive_key("APP_NAME") is False
    assert is_sensitive_key("PORT") is False


def test_is_sensitive_key_case_insensitive_by_default():
    assert is_sensitive_key("db_password") is True


def test_is_sensitive_key_case_sensitive_no_match():
    assert is_sensitive_key("db_password", case_sensitive=True) is False


def test_is_sensitive_key_custom_patterns():
    assert is_sensitive_key("MY_PIN", patterns=[r".*PIN.*"]) is True
    assert is_sensitive_key("APP_NAME", patterns=[r".*PIN.*"]) is False


# ---------------------------------------------------------------------------
# redact_value
# ---------------------------------------------------------------------------

def test_redact_value_returns_placeholder():
    assert redact_value("supersecret") == REDACT_PLACEHOLDER


def test_redact_value_empty_string():
    assert redact_value("") == REDACT_PLACEHOLDER


def test_redact_value_reveals_trailing_chars():
    result = redact_value("supersecret", reveal_chars=3)
    assert result.endswith("ret")
    assert result.startswith(REDACT_PLACEHOLDER)


def test_redact_value_reveal_chars_exceeds_length():
    # When reveal_chars >= len(value), full placeholder is returned
    result = redact_value("abc", reveal_chars=5)
    assert result == REDACT_PLACEHOLDER


def test_redact_value_custom_placeholder():
    assert redact_value("secret", placeholder="[hidden]") == "[hidden]"


# ---------------------------------------------------------------------------
# redact_env
# ---------------------------------------------------------------------------

def test_redact_env_masks_sensitive_keys():
    env = {"APP_NAME": "myapp", "DB_PASSWORD": "s3cr3t", "PORT": "8080"}
    result = redact_env(env)
    assert result["APP_NAME"] == "myapp"
    assert result["PORT"] == "8080"
    assert result["DB_PASSWORD"] == REDACT_PLACEHOLDER


def test_redact_env_empty_dict():
    assert redact_env({}) == {}


def test_redact_env_all_non_sensitive():
    env = {"HOST": "localhost", "PORT": "5432"}
    assert redact_env(env) == env


def test_redact_env_does_not_mutate_original():
    env = {"DB_PASSWORD": "secret"}
    redact_env(env)
    assert env["DB_PASSWORD"] == "secret"


# ---------------------------------------------------------------------------
# list_sensitive_keys
# ---------------------------------------------------------------------------

def test_list_sensitive_keys_returns_sorted():
    env = {"PORT": "80", "DB_SECRET": "x", "API_KEY": "y", "HOST": "h"}
    keys = list_sensitive_keys(env)
    assert keys == sorted(["DB_SECRET", "API_KEY"])


def test_list_sensitive_keys_empty_env():
    assert list_sensitive_keys({}) == []


def test_list_sensitive_keys_none_sensitive():
    env = {"HOST": "localhost", "PORT": "5432"}
    assert list_sensitive_keys(env) == []
