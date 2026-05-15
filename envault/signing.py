"""Signing module: sign and verify env dicts using HMAC-SHA256."""

import hashlib
import hmac
import json
from typing import Dict

SIGNATURE_KEY = "__envault_sig__"


def _canonical(env: Dict[str, str]) -> bytes:
    """Produce a stable canonical bytes representation of an env dict."""
    # Sort keys to ensure order-independent signing
    ordered = {k: env[k] for k in sorted(env)}
    return json.dumps(ordered, separators=(",", ":"), sort_keys=True).encode()


def sign_env(env: Dict[str, str], secret: bytes) -> str:
    """Return an HMAC-SHA256 hex digest for the given env dict."""
    if not isinstance(secret, bytes):
        raise TypeError("secret must be bytes")
    payload = _canonical(env)
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


def attach_signature(env: Dict[str, str], secret: bytes) -> Dict[str, str]:
    """Return a copy of env with the signature embedded under SIGNATURE_KEY."""
    clean = {k: v for k, v in env.items() if k != SIGNATURE_KEY}
    sig = sign_env(clean, secret)
    result = dict(clean)
    result[SIGNATURE_KEY] = sig
    return result


def verify_signature(env: Dict[str, str], secret: bytes) -> bool:
    """Return True if the embedded signature matches the env contents."""
    if SIGNATURE_KEY not in env:
        return False
    stored_sig = env[SIGNATURE_KEY]
    clean = {k: v for k, v in env.items() if k != SIGNATURE_KEY}
    expected = sign_env(clean, secret)
    return hmac.compare_digest(stored_sig, expected)


def strip_signature(env: Dict[str, str]) -> Dict[str, str]:
    """Return a copy of env without the signature key."""
    return {k: v for k, v in env.items() if k != SIGNATURE_KEY}
