"""Prune unused or stale keys from an env dict based on various criteria."""

from __future__ import annotations

import fnmatch
import re
from typing import Dict, List, Optional, Tuple


class PruneError(Exception):
    """Raised when a prune operation cannot be completed."""


def prune_by_keys(
    env: Dict[str, str],
    keys: List[str],
    *,
    missing_ok: bool = True,
) -> Tuple[Dict[str, str], List[str]]:
    """Remove specific keys from *env*.

    Returns (new_env, removed_keys).  If *missing_ok* is False, raises
    PruneError for any key that does not exist in *env*.
    """
    if not missing_ok:
        missing = [k for k in keys if k not in env]
        if missing:
            raise PruneError(f"Keys not found in env: {missing}")

    result = dict(env)
    removed: List[str] = []
    for k in keys:
        if k in result:
            del result[k]
            removed.append(k)
    return result, removed


def prune_by_glob(
    env: Dict[str, str],
    pattern: str,
    *,
    case_sensitive: bool = False,
) -> Tuple[Dict[str, str], List[str]]:
    """Remove all keys matching *pattern* (glob syntax)."""
    result: Dict[str, str] = {}
    removed: List[str] = []
    for k, v in env.items():
        candidate = k if case_sensitive else k.upper()
        pat = pattern if case_sensitive else pattern.upper()
        if fnmatch.fnmatchcase(candidate, pat):
            removed.append(k)
        else:
            result[k] = v
    return result, removed


def prune_by_regex(
    env: Dict[str, str],
    pattern: str,
    *,
    flags: int = re.IGNORECASE,
) -> Tuple[Dict[str, str], List[str]]:
    """Remove all keys whose name matches the regular expression *pattern*."""
    try:
        rx = re.compile(pattern, flags)
    except re.error as exc:
        raise PruneError(f"Invalid regex pattern '{pattern}': {exc}") from exc

    result: Dict[str, str] = {}
    removed: List[str] = []
    for k, v in env.items():
        if rx.search(k):
            removed.append(k)
        else:
            result[k] = v
    return result, removed


def prune_empty(
    env: Dict[str, str],
    *,
    strip: bool = True,
) -> Tuple[Dict[str, str], List[str]]:
    """Remove keys whose value is empty (or whitespace-only when *strip* is True)."""
    result: Dict[str, str] = {}
    removed: List[str] = []
    for k, v in env.items():
        check = v.strip() if strip else v
        if check == "":
            removed.append(k)
        else:
            result[k] = v
    return result, removed


def prune_report(
    removed: List[str],
    *,
    total_before: Optional[int] = None,
) -> Dict[str, object]:
    """Build a human-friendly report dict for a prune operation."""
    report: Dict[str, object] = {
        "removed": removed,
        "count": len(removed),
    }
    if total_before is not None:
        report["remaining"] = total_before - len(removed)
    return report
