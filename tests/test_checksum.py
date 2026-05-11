"""Tests for envault.checksum module."""

import pytest
from envault.checksum import (
    compute_checksum,
    save_checksum,
    load_checksum,
    verify_checksum,
    delete_checksum,
)


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


ENV_A = {"DB_HOST": "localhost", "PORT": "5432"}
ENV_B = {"DB_HOST": "remotehost", "PORT": "5432"}


def test_compute_checksum_returns_hex_string():
    digest = compute_checksum(ENV_A)
    assert isinstance(digest, str)
    assert len(digest) == 64


def test_compute_checksum_is_deterministic():
    assert compute_checksum(ENV_A) == compute_checksum(ENV_A)


def test_compute_checksum_order_independent():
    env1 = {"A": "1", "B": "2"}
    env2 = {"B": "2", "A": "1"}
    assert compute_checksum(env1) == compute_checksum(env2)


def test_compute_checksum_differs_for_different_envs():
    assert compute_checksum(ENV_A) != compute_checksum(ENV_B)


def test_save_checksum_returns_digest(base_dir):
    digest = save_checksum("myproject", ENV_A, base_dir=base_dir)
    assert digest == compute_checksum(ENV_A)


def test_load_checksum_after_save(base_dir):
    save_checksum("myproject", ENV_A, base_dir=base_dir)
    loaded = load_checksum("myproject", base_dir=base_dir)
    assert loaded == compute_checksum(ENV_A)


def test_load_checksum_missing_returns_none(base_dir):
    result = load_checksum("nonexistent", base_dir=base_dir)
    assert result is None


def test_verify_checksum_passes_when_env_unchanged(base_dir):
    save_checksum("proj", ENV_A, base_dir=base_dir)
    assert verify_checksum("proj", ENV_A, base_dir=base_dir) is True


def test_verify_checksum_fails_when_env_changed(base_dir):
    save_checksum("proj", ENV_A, base_dir=base_dir)
    assert verify_checksum("proj", ENV_B, base_dir=base_dir) is False


def test_verify_checksum_returns_false_when_no_stored(base_dir):
    assert verify_checksum("ghost", ENV_A, base_dir=base_dir) is False


def test_delete_checksum_returns_true_when_exists(base_dir):
    save_checksum("proj", ENV_A, base_dir=base_dir)
    assert delete_checksum("proj", base_dir=base_dir) is True


def test_delete_checksum_returns_false_when_missing(base_dir):
    assert delete_checksum("ghost", base_dir=base_dir) is False


def test_delete_checksum_removes_file(base_dir):
    save_checksum("proj", ENV_A, base_dir=base_dir)
    delete_checksum("proj", base_dir=base_dir)
    assert load_checksum("proj", base_dir=base_dir) is None
