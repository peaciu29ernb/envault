"""condense.py — Reduce an env dict by removing duplicate values and optionally filtering keys."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple


def find_duplicate_values(env: Dict[str, str]) -> Dict[str, List[str]]:
    """Return a mapping of value -> list of keys that share that value.

    Only values that appear more than once are included.
    """
    value_map: Dict[str, List[str]] = {}
    for key, value in env.items():
        value_map.setdefault(value, []).append(key)
    return {v: keys for v, keys in value_map.items() if len(keys) > 1}


def deduplicate_values(
    env: Dict[str, str],
    keep: str = "first",
) -> Tuple[Dict[str, str], List[str]]:
    """Remove keys whose values are duplicated, keeping one representative.

    Args:
        env: The source environment dict.
        keep: ``"first"`` keeps the lexicographically first key;
              ``"last"`` keeps the last.

    Returns:
        A tuple of (condensed_dict, list_of_removed_keys).
    """
    duplicates = find_duplicate_values(env)
    keys_to_remove: set[str] = set()
    for value, keys in duplicates.items():
        sorted_keys = sorted(keys)
        if keep == "last":
            sorted_keys = list(reversed(sorted_keys))
        # Drop all but the first in sorted order
        for k in sorted_keys[1:]:
            keys_to_remove.add(k)

    condensed = {k: v for k, v in env.items() if k not in keys_to_remove}
    return condensed, sorted(keys_to_remove)


def drop_empty_values(env: Dict[str, str]) -> Tuple[Dict[str, str], List[str]]:
    """Remove keys whose value is an empty string.

    Returns:
        A tuple of (filtered_dict, list_of_removed_keys).
    """
    removed = [k for k, v in env.items() if v == ""]
    filtered = {k: v for k, v in env.items() if v != ""}
    return filtered, removed


def condense(
    env: Dict[str, str],
    remove_empty: bool = True,
    deduplicate: bool = True,
    keep: str = "first",
) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    """Apply all condensation passes to *env*.

    Args:
        env: Source environment dict.
        remove_empty: Drop keys with empty string values.
        deduplicate: Drop keys with duplicate values.
        keep: Which key to retain when deduplicating (``"first"`` or ``"last"``)

    Returns:
        A tuple of (condensed_dict, report) where *report* is a dict with
        keys ``"empty_removed"`` and ``"duplicate_removed"``.
    """
    report: Dict[str, List[str]] = {"empty_removed": [], "duplicate_removed": []}
    result = dict(env)

    if remove_empty:
        result, empty_keys = drop_empty_values(result)
        report["empty_removed"] = empty_keys

    if deduplicate:
        result, dup_keys = deduplicate_values(result, keep=keep)
        report["duplicate_removed"] = dup_keys

    return result, report
