"""Tests for envault.signing module."""

import pytest
from envault.signing import (
    sign_env,
    attach_signature,
    verify_signature,
    strip_signature,
    SIGNATURE_KEY,
)

SECRET = b"supersecretkey1234567890abcdef12"
SAMPLE_ENV = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_KEY": "abc"}


def test_sign_env_returns_hex_string():
    sig = sign_env(SAMPLE_ENV, SECRET)
    assert isinstance(sig, str)
    assert len(sig) == 64  # SHA-256 hex digest


def test_sign_env_is_deterministic():
    sig1 = sign_env(SAMPLE_ENV, SECRET)
    sig2 = sign_env(SAMPLE_ENV, SECRET)
    assert sig1 == sig2


def test_sign_env_order_independent():
    env_a = {"A": "1", "B": "2"}
    env_b = {"B": "2", "A": "1"}
    assert sign_env(env_a, SECRET) == sign_env(env_b, SECRET)


def test_sign_env_different_secret_differs():
    sig1 = sign_env(SAMPLE_ENV, SECRET)
    sig2 = sign_env(SAMPLE_ENV, b"differentsecretkey1234567890xyz")
    assert sig1 != sig2


def test_sign_env_requires_bytes_secret():
    with pytest.raises(TypeError):
        sign_env(SAMPLE_ENV, "notbytes")


def test_attach_signature_adds_key():
    signed = attach_signature(SAMPLE_ENV, SECRET)
    assert SIGNATURE_KEY in signed


def test_attach_signature_does_not_mutate_original():
    original = dict(SAMPLE_ENV)
    attach_signature(SAMPLE_ENV, SECRET)
    assert SIGNATURE_KEY not in original


def test_attach_signature_excludes_previous_sig():
    signed_once = attach_signature(SAMPLE_ENV, SECRET)
    signed_twice = attach_signature(signed_once, SECRET)
    # Signature should be identical since inner sig is stripped before re-signing
    assert signed_once[SIGNATURE_KEY] == signed_twice[SIGNATURE_KEY]


def test_verify_signature_valid():
    signed = attach_signature(SAMPLE_ENV, SECRET)
    assert verify_signature(signed, SECRET) is True


def test_verify_signature_wrong_secret():
    signed = attach_signature(SAMPLE_ENV, SECRET)
    assert verify_signature(signed, b"wrongkey" * 4) is False


def test_verify_signature_tampered_env():
    signed = attach_signature(SAMPLE_ENV, SECRET)
    signed["INJECTED"] = "evil"
    assert verify_signature(signed, SECRET) is False


def test_verify_signature_missing_sig_returns_false():
    assert verify_signature(SAMPLE_ENV, SECRET) is False


def test_strip_signature_removes_key():
    signed = attach_signature(SAMPLE_ENV, SECRET)
    stripped = strip_signature(signed)
    assert SIGNATURE_KEY not in stripped


def test_strip_signature_preserves_other_keys():
    signed = attach_signature(SAMPLE_ENV, SECRET)
    stripped = strip_signature(signed)
    assert stripped == SAMPLE_ENV
