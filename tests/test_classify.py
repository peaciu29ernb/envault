"""Tests for envault.classify."""

import pytest
from envault.classify import classify_key, classify_env, keys_in_category, list_categories


# --- classify_key ---

def test_classify_key_database():
    assert classify_key("DB_HOST") == "database"
    assert classify_key("DATABASE_URL") == "database"
    assert classify_key("POSTGRES_PASSWORD") == "database"


def test_classify_key_auth():
    assert classify_key("JWT_SECRET") == "auth"
    assert classify_key("AUTH_TOKEN") == "auth"
    assert classify_key("OAUTH_CLIENT_ID") == "auth"


def test_classify_key_api():
    assert classify_key("API_KEY") == "api"
    assert classify_key("SERVICE_URL") == "api"
    assert classify_key("BASE_URL") == "api"


def test_classify_key_cloud():
    assert classify_key("AWS_ACCESS_KEY_ID") == "cloud"
    assert classify_key("GCP_PROJECT") == "cloud"
    assert classify_key("AZURE_TENANT_ID") == "cloud"


def test_classify_key_logging():
    assert classify_key("LOG_LEVEL") == "logging"
    assert classify_key("SENTRY_DSN") == "logging"


def test_classify_key_feature():
    assert classify_key("FEATURE_FLAG_X") == "feature"
    assert classify_key("ENABLE_BETA") == "feature"


def test_classify_key_app():
    assert classify_key("APP_NAME") == "app"
    assert classify_key("PORT") == "app"
    assert classify_key("DEBUG") == "app"


def test_classify_key_unknown_returns_none():
    assert classify_key("MY_RANDOM_VARIABLE") is None
    assert classify_key("FOOBAR") is None


def test_classify_key_custom_categories():
    custom = {"infra": [r"INFRA_", r"K8S_"]}
    assert classify_key("K8S_NAMESPACE", custom) == "infra"
    assert classify_key("DB_HOST", custom) is None


# --- classify_env ---

def test_classify_env_groups_keys():
    env = {
        "DB_HOST": "localhost",
        "API_KEY": "abc",
        "UNKNOWN_VAR": "x",
    }
    result = classify_env(env)
    assert "DB_HOST" in result["database"]
    assert "API_KEY" in result["api"]
    assert "UNKNOWN_VAR" in result["uncategorized"]


def test_classify_env_empty():
    assert classify_env({}) == {}


def test_classify_env_all_uncategorized():
    env = {"FOO": "1", "BAR": "2"}
    result = classify_env(env)
    assert set(result.keys()) == {"uncategorized"}
    assert sorted(result["uncategorized"]) == ["BAR", "FOO"]


def test_classify_env_keys_sorted():
    env = {"DB_Z": "1", "DB_A": "2", "DB_M": "3"}
    result = classify_env(env)
    assert result["database"] == ["DB_A", "DB_M", "DB_Z"]


# --- keys_in_category ---

def test_keys_in_category_returns_matching():
    env = {"AWS_KEY": "x", "DB_URL": "y", "PORT": "8080"}
    assert keys_in_category(env, "cloud") == ["AWS_KEY"]


def test_keys_in_category_missing_category_returns_empty():
    env = {"PORT": "8080"}
    assert keys_in_category(env, "cloud") == []


# --- list_categories ---

def test_list_categories_returns_sorted():
    cats = list_categories()
    assert cats == sorted(cats)
    assert "database" in cats
    assert "auth" in cats


def test_list_categories_custom():
    custom = {"z_group": [], "a_group": []}
    assert list_categories(custom) == ["a_group", "z_group"]
