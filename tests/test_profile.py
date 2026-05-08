"""Tests for envault.profile module."""

from __future__ import annotations

import pytest

from envault.profile import (
    delete_profile,
    diff_profiles,
    list_profiles,
    load_profile,
    save_profile,
)


@pytest.fixture
def base_dir(tmp_path):
    return tmp_path / "profiles"


def test_save_and_load_profile(base_dir):
    data = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    save_profile("myapp", "dev", data, base_dir=base_dir)
    loaded = load_profile("myapp", "dev", base_dir=base_dir)
    assert loaded == data


def test_save_profile_returns_path(base_dir):
    path = save_profile("myapp", "dev", {"KEY": "val"}, base_dir=base_dir)
    assert path.exists()
    assert path.suffix == ".json"


def test_load_missing_profile_raises(base_dir):
    with pytest.raises(FileNotFoundError, match="staging"):
        load_profile("myapp", "staging", base_dir=base_dir)


def test_list_profiles_empty(base_dir):
    assert list_profiles("myapp", base_dir=base_dir) == []


def test_list_profiles_multiple(base_dir):
    for name in ("dev", "prod", "staging"):
        save_profile("myapp", name, {"ENV": name}, base_dir=base_dir)
    profiles = list_profiles("myapp", base_dir=base_dir)
    assert profiles == ["dev", "prod", "staging"]


def test_delete_profile_returns_true(base_dir):
    save_profile("myapp", "dev", {}, base_dir=base_dir)
    assert delete_profile("myapp", "dev", base_dir=base_dir) is True
    assert "dev" not in list_profiles("myapp", base_dir=base_dir)


def test_delete_missing_profile_returns_false(base_dir):
    assert delete_profile("myapp", "ghost", base_dir=base_dir) is False


def test_diff_profiles_added_key(base_dir):
    save_profile("myapp", "dev", {"A": "1"}, base_dir=base_dir)
    save_profile("myapp", "prod", {"A": "1", "B": "2"}, base_dir=base_dir)
    diff = diff_profiles("myapp", "dev", "prod", base_dir=base_dir)
    assert "B" in diff
    assert diff["B"]["status"] == "added"


def test_diff_profiles_removed_key(base_dir):
    save_profile("myapp", "dev", {"A": "1", "B": "2"}, base_dir=base_dir)
    save_profile("myapp", "prod", {"A": "1"}, base_dir=base_dir)
    diff = diff_profiles("myapp", "dev", "prod", base_dir=base_dir)
    assert diff["B"]["status"] == "removed"


def test_diff_profiles_changed_key(base_dir):
    save_profile("myapp", "dev", {"URL": "http://dev"}, base_dir=base_dir)
    save_profile("myapp", "prod", {"URL": "https://prod"}, base_dir=base_dir)
    diff = diff_profiles("myapp", "dev", "prod", base_dir=base_dir)
    assert diff["URL"]["status"] == "changed"
    assert diff["URL"]["from"] == "http://dev"
    assert diff["URL"]["to"] == "https://prod"


def test_diff_profiles_identical(base_dir):
    env = {"X": "1", "Y": "2"}
    save_profile("myapp", "a", env, base_dir=base_dir)
    save_profile("myapp", "b", env, base_dir=base_dir)
    assert diff_profiles("myapp", "a", "b", base_dir=base_dir) == {}
