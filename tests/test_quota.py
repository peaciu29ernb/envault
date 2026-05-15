"""Tests for envault.quota module."""

import pytest
from envault.quota import (
    set_quota,
    get_quota,
    remove_quota,
    check_quota,
    list_quotas,
    DEFAULT_QUOTA,
)


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def test_get_quota_returns_default_when_not_set(base_dir):
    assert get_quota("myproject", base_dir) == DEFAULT_QUOTA


def test_set_quota_stores_limit(base_dir):
    result = set_quota("myproject", 50, base_dir)
    assert result == 50
    assert get_quota("myproject", base_dir) == 50


def test_set_quota_overwrites_existing(base_dir):
    set_quota("myproject", 50, base_dir)
    set_quota("myproject", 75, base_dir)
    assert get_quota("myproject", base_dir) == 75


def test_set_quota_invalid_raises(base_dir):
    with pytest.raises(ValueError, match="at least 1"):
        set_quota("myproject", 0, base_dir)


def test_set_quota_negative_raises(base_dir):
    with pytest.raises(ValueError):
        set_quota("myproject", -10, base_dir)


def test_remove_quota_returns_true(base_dir):
    set_quota("myproject", 30, base_dir)
    assert remove_quota("myproject", base_dir) is True
    assert get_quota("myproject", base_dir) == DEFAULT_QUOTA


def test_remove_quota_missing_returns_false(base_dir):
    assert remove_quota("nonexistent", base_dir) is False


def test_check_quota_within_limit(base_dir):
    set_quota("proj", 10, base_dir)
    assert check_quota("proj", 5, base_dir) is True
    assert check_quota("proj", 10, base_dir) is True


def test_check_quota_exceeds_limit(base_dir):
    set_quota("proj", 10, base_dir)
    assert check_quota("proj", 11, base_dir) is False


def test_check_quota_uses_default_when_not_set(base_dir):
    assert check_quota("proj", DEFAULT_QUOTA, base_dir) is True
    assert check_quota("proj", DEFAULT_QUOTA + 1, base_dir) is False


def test_list_quotas_empty(base_dir):
    assert list_quotas(base_dir) == {}


def test_list_quotas_multiple_projects(base_dir):
    set_quota("alpha", 20, base_dir)
    set_quota("beta", 40, base_dir)
    result = list_quotas(base_dir)
    assert result == {"alpha": 20, "beta": 40}


def test_list_quotas_after_remove(base_dir):
    set_quota("alpha", 20, base_dir)
    set_quota("beta", 40, base_dir)
    remove_quota("alpha", base_dir)
    assert list_quotas(base_dir) == {"beta": 40}
