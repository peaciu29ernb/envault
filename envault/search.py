"""Search and filter utilities for vault environment variables."""

from __future__ import annotations

import fnmatch
import re
from typing import Dict, List, Optional


def search_keys(
    env: Dict[str, str],
    pattern: str,
    *,
    use_regex: bool = False,
    case_sensitive: bool = False,
) -> Dict[str, str]:
    """Return entries whose keys match *pattern*.

    Args:
        env: Flat key/value mapping.
        pattern: Glob (default) or regex string.
        use_regex: Treat *pattern* as a regular expression.
        case_sensitive: Whether matching is case-sensitive.

    Returns:
        Filtered dict with only the matching keys.
    """
    flags = 0 if case_sensitive else re.IGNORECASE

    if use_regex:
        compiled = re.compile(pattern, flags)
        return {k: v for k, v in env.items() if compiled.search(k)}

    if not case_sensitive:
        return {
            k: v
            for k, v in env.items()
            if fnmatch.fnmatchcase(k.lower(), pattern.lower())
        }
    return {k: v for k, v in env.items() if fnmatch.fnmatchcase(k, pattern)}


def search_values(
    env: Dict[str, str],
    pattern: str,
    *,
    use_regex: bool = False,
    case_sensitive: bool = False,
) -> Dict[str, str]:
    """Return entries whose values contain *pattern*."""
    flags = 0 if case_sensitive else re.IGNORECASE

    if use_regex:
        compiled = re.compile(pattern, flags)
        return {k: v for k, v in env.items() if compiled.search(v)}

    needle = pattern if case_sensitive else pattern.lower()
    return {
        k: v
        for k, v in env.items()
        if needle in (v if case_sensitive else v.lower())
    }


def filter_by_prefix(env: Dict[str, str], prefix: str) -> Dict[str, str]:
    """Return only keys that start with *prefix* (case-insensitive)."""
    p = prefix.upper()
    return {k: v for k, v in env.items() if k.upper().startswith(p)}


def list_keys(env: Dict[str, str], sort: bool = True) -> List[str]:
    """Return all keys, optionally sorted."""
    keys = list(env.keys())
    return sorted(keys) if sort else keys
