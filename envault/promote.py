"""Promote env vars from one environment profile to another with optional filtering."""

from __future__ import annotations

from typing import Dict, List, Optional


class PromoteError(Exception):
    """Raised when a promotion operation fails."""


def promote_keys(
    source: Dict[str, str],
    target: Dict[str, str],
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
    exclude: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Promote keys from *source* into *target*.

    Args:
        source: The source environment dict.
        target: The target environment dict (not mutated).
        keys: If given, only these keys are promoted. Promotes all if None.
        overwrite: When True, existing keys in target are overwritten.
        exclude: Keys to skip even if they appear in *keys* or source.

    Returns:
        A new dict representing the merged result.
    """
    exclude_set = set(exclude or [])
    candidates = keys if keys is not None else list(source.keys())

    result = dict(target)
    for key in candidates:
        if key in exclude_set:
            continue
        if key not in source:
            raise PromoteError(f"Key '{key}' not found in source environment.")
        if key in result and not overwrite:
            continue
        result[key] = source[key]
    return result


def promote_report(
    source: Dict[str, str],
    target: Dict[str, str],
    promoted: Dict[str, str],
) -> List[Dict[str, str]]:
    """Build a human-readable report of what changed during promotion."""
    report = []
    for key, value in promoted.items():
        if key not in target:
            report.append({"key": key, "action": "added", "value": value})
        elif target[key] != value:
            report.append({"key": key, "action": "overwritten",
                           "old": target[key], "value": value})
        else:
            report.append({"key": key, "action": "unchanged", "value": value})
    return report
