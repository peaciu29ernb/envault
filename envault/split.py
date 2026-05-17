"""Split an env dict into multiple named partitions based on key patterns."""

from __future__ import annotations

import fnmatch
import re
from typing import Dict, List, Optional, Tuple


class SplitError(Exception):
    """Raised when a split operation cannot be completed."""


SplitResult = Dict[str, Dict[str, str]]


def split_by_prefix(
    env: Dict[str, str],
    prefixes: List[str],
    *,
    remainder_key: Optional[str] = "__rest__",
    strip_prefix: bool = False,
) -> SplitResult:
    """Partition *env* into buckets based on key prefixes.

    Keys are matched against *prefixes* in order; the first match wins.
    Unmatched keys go into *remainder_key* (omitted when ``None``).
    If *strip_prefix* is True the prefix is removed from the key in the bucket.
    """
    result: SplitResult = {p: {} for p in prefixes}
    rest: Dict[str, str] = {}

    for key, value in env.items():
        matched = False
        for prefix in prefixes:
            if key.startswith(prefix):
                out_key = key[len(prefix):] if strip_prefix else key
                result[prefix][out_key] = value
                matched = True
                break
        if not matched:
            rest[key] = value

    if remainder_key is not None:
        result[remainder_key] = rest

    return result


def split_by_glob(
    env: Dict[str, str],
    patterns: Dict[str, str],
    *,
    remainder_key: Optional[str] = "__rest__",
) -> SplitResult:
    """Partition *env* using glob patterns.

    *patterns* maps bucket_name -> glob_pattern.
    First matching pattern wins.
    """
    result: SplitResult = {name: {} for name in patterns}
    rest: Dict[str, str] = {}

    for key, value in env.items():
        matched = False
        for name, pattern in patterns.items():
            if fnmatch.fnmatchcase(key, pattern):
                result[name][key] = value
                matched = True
                break
        if not matched:
            rest[key] = value

    if remainder_key is not None:
        result[remainder_key] = rest

    return result


def split_by_regex(
    env: Dict[str, str],
    patterns: Dict[str, str],
    *,
    remainder_key: Optional[str] = "__rest__",
) -> SplitResult:
    """Partition *env* using regex patterns.

    *patterns* maps bucket_name -> regex_string.
    First matching pattern wins.
    """
    compiled: List[Tuple[str, re.Pattern]] = []
    for name, pat in patterns.items():
        try:
            compiled.append((name, re.compile(pat)))
        except re.error as exc:
            raise SplitError(f"Invalid regex for bucket '{name}': {exc}") from exc

    result: SplitResult = {name: {} for name, _ in compiled}
    rest: Dict[str, str] = {}

    for key, value in env.items():
        matched = False
        for name, rx in compiled:
            if rx.search(key):
                result[name][key] = value
                matched = True
                break
        if not matched:
            rest[key] = value

    if remainder_key is not None:
        result[remainder_key] = rest

    return result
