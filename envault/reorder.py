"""Reorder keys in an env dict by various strategies."""

from __future__ import annotations

from typing import Dict, List, Optional


class ReorderError(Exception):
    """Raised when a reorder operation cannot be completed."""


def reorder_alphabetical(env: Dict[str, str], reverse: bool = False) -> Dict[str, str]:
    """Return a new dict with keys sorted alphabetically."""
    return dict(sorted(env.items(), key=lambda kv: kv[0], reverse=reverse))


def reorder_by_list(env: Dict[str, str], order: List[str], append_rest: bool = True) -> Dict[str, str]:
    """Return a new dict reordered so that *order* keys come first.

    Args:
        env: Source environment dict.
        order: Desired key ordering.  Keys not present in *env* are silently skipped.
        append_rest: When True, keys in *env* that are not in *order* are
            appended at the end in their original relative order.

    Raises:
        ReorderError: If *append_rest* is False and *env* contains keys not
            listed in *order*.
    """
    result: Dict[str, str] = {}
    for key in order:
        if key in env:
            result[key] = env[key]

    remaining = {k: v for k, v in env.items() if k not in result}
    if remaining and not append_rest:
        missing = ", ".join(sorted(remaining))
        raise ReorderError(
            f"Keys not covered by order list (append_rest=False): {missing}"
        )
    result.update(remaining)
    return result


def reorder_by_prefix(env: Dict[str, str], prefixes: List[str], append_rest: bool = True) -> Dict[str, str]:
    """Group keys by prefix order, then append remaining keys.

    Keys matching the first prefix appear first, then the second prefix, etc.
    Within each group the original relative order is preserved.
    """
    groups: Dict[str, Dict[str, str]] = {p: {} for p in prefixes}
    rest: Dict[str, str] = {}

    for key, value in env.items():
        matched = False
        for prefix in prefixes:
            if key.startswith(prefix):
                groups[prefix][key] = value
                matched = True
                break
        if not matched:
            rest[key] = value

    result: Dict[str, str] = {}
    for prefix in prefixes:
        result.update(groups[prefix])
    if append_rest:
        result.update(rest)
    return result


def move_to_top(env: Dict[str, str], keys: List[str]) -> Dict[str, str]:
    """Move specific keys to the top of the dict, preserving rest order."""
    top = {k: env[k] for k in keys if k in env}
    rest = {k: v for k, v in env.items() if k not in top}
    return {**top, **rest}


def move_to_bottom(env: Dict[str, str], keys: List[str]) -> Dict[str, str]:
    """Move specific keys to the bottom of the dict, preserving rest order."""
    bottom = {k: env[k] for k in keys if k in env}
    rest = {k: v for k, v in env.items() if k not in bottom}
    return {**rest, **bottom}
