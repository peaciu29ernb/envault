"""Summarize an env dict with statistics and categorized counts."""

from __future__ import annotations

from typing import Any


_SENSITIVE_PATTERNS = ("password", "secret", "token", "key", "api", "auth", "private")


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(p in lower for p in _SENSITIVE_PATTERNS)


def count_keys(env: dict[str, str]) -> int:
    """Return total number of keys."""
    return len(env)


def count_empty(env: dict[str, str]) -> int:
    """Return number of keys with empty string values."""
    return sum(1 for v in env.values() if v == "")


def count_sensitive(env: dict[str, str]) -> int:
    """Return number of keys that look sensitive."""
    return sum(1 for k in env if _is_sensitive(k))


def average_value_length(env: dict[str, str]) -> float:
    """Return average character length of values (0.0 for empty env)."""
    if not env:
        return 0.0
    return sum(len(v) for v in env.values()) / len(env)


def longest_key(env: dict[str, str]) -> str | None:
    """Return the key with the longest name, or None if env is empty."""
    if not env:
        return None
    return max(env, key=lambda k: len(k))


def summarize(env: dict[str, str]) -> dict[str, Any]:
    """Return a summary dict with statistics about *env*."""
    total = count_keys(env)
    empty = count_empty(env)
    sensitive = count_sensitive(env)
    avg_len = average_value_length(env)
    top_key = longest_key(env)

    return {
        "total_keys": total,
        "empty_values": empty,
        "non_empty_values": total - empty,
        "sensitive_keys": sensitive,
        "average_value_length": round(avg_len, 2),
        "longest_key": top_key,
    }
