"""Filter env dicts by various criteria."""

from __future__ import annotations

import fnmatch
import re
from typing import Dict, List, Optional


class FilterError(Exception):
    """Raised when a filter operation fails."""


def filter_by_keys(env: Dict[str, str], keys: List[str]) -> Dict[str, str]:
    """Return only the entries whose key is in *keys*."""
    key_set = set(keys)
    return {k: v for k, v in env.items() if k in key_set}


def exclude_by_keys(env: Dict[str, str], keys: List[str]) -> Dict[str, str]:
    """Return entries whose key is NOT in *keys*."""
    key_set = set(keys)
    return {k: v for k, v in env.items() if k not in key_set}


def filter_by_glob(env: Dict[str, str], pattern: str, *, case_sensitive: bool = False) -> Dict[str, str]:
    """Return entries whose key matches the glob *pattern*."""
    result: Dict[str, str] = {}
    for k, v in env.items():
        target = k if case_sensitive else k.upper()
        pat = pattern if case_sensitive else pattern.upper()
        if fnmatch.fnmatchcase(target, pat):
            result[k] = v
    return result


def filter_by_regex(env: Dict[str, str], pattern: str, *, flags: int = re.IGNORECASE) -> Dict[str, str]:
    """Return entries whose key matches the regex *pattern*."""
    try:
        compiled = re.compile(pattern, flags)
    except re.error as exc:
        raise FilterError(f"Invalid regex pattern '{pattern}': {exc}") from exc
    return {k: v for k, v in env.items() if compiled.search(k)}


def filter_by_value(env: Dict[str, str], pattern: str, *, flags: int = re.IGNORECASE) -> Dict[str, str]:
    """Return entries whose value matches the regex *pattern*."""
    try:
        compiled = re.compile(pattern, flags)
    except re.error as exc:
        raise FilterError(f"Invalid regex pattern '{pattern}': {exc}") from exc
    return {k: v for k, v in env.items() if compiled.search(v)}


def filter_non_empty(env: Dict[str, str]) -> Dict[str, str]:
    """Return entries with non-empty string values."""
    return {k: v for k, v in env.items() if v.strip()}


def filter_env(
    env: Dict[str, str],
    *,
    include_keys: Optional[List[str]] = None,
    exclude_keys: Optional[List[str]] = None,
    glob: Optional[str] = None,
    regex: Optional[str] = None,
    non_empty: bool = False,
) -> Dict[str, str]:
    """Composite filter: apply multiple criteria in sequence."""
    result = dict(env)
    if include_keys is not None:
        result = filter_by_keys(result, include_keys)
    if exclude_keys is not None:
        result = exclude_by_keys(result, exclude_keys)
    if glob is not None:
        result = filter_by_glob(result, glob)
    if regex is not None:
        result = filter_by_regex(result, regex)
    if non_empty:
        result = filter_non_empty(result)
    return result
