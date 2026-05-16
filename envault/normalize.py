"""Normalize environment variable keys and values.

Provides utilities for standardizing the shape of env dicts:
- key normalization (upper-case, strip whitespace, replace hyphens)
- value normalization (strip surrounding whitespace, collapse internal whitespace)
- full env normalization in one pass
"""

from __future__ import annotations

import re
from typing import Dict, Optional


class NormalizeError(Exception):
    """Raised when normalization cannot be applied."""


def normalize_key(key: str, *, upper: bool = True, replace_hyphens: bool = True) -> str:
    """Return a normalized version of *key*.

    Steps applied in order:
    1. Strip leading/trailing whitespace.
    2. Replace hyphens with underscores (when *replace_hyphens* is True).
    3. Convert to upper-case (when *upper* is True).

    Raises NormalizeError if the result is an empty string.
    """
    result = key.strip()
    if replace_hyphens:
        result = result.replace("-", "_")
    if upper:
        result = result.upper()
    if not result:
        raise NormalizeError("Key is empty after normalization.")
    return result


def normalize_value(
    value: str,
    *,
    strip: bool = True,
    collapse_whitespace: bool = False,
) -> str:
    """Return a normalized version of *value*.

    Steps applied in order:
    1. Strip leading/trailing whitespace (when *strip* is True).
    2. Collapse runs of internal whitespace to a single space
       (when *collapse_whitespace* is True).
    """
    result = value.strip() if strip else value
    if collapse_whitespace:
        result = re.sub(r"\s+", " ", result)
    return result


def normalize_env(
    env: Dict[str, str],
    *,
    upper: bool = True,
    replace_hyphens: bool = True,
    strip_values: bool = True,
    collapse_whitespace: bool = False,
    on_conflict: str = "error",
) -> Dict[str, str]:
    """Return a new dict with all keys and values normalized.

    *on_conflict* controls what happens when two source keys map to the
    same normalized key:
    - ``"error"``  – raise NormalizeError (default)
    - ``"first"``  – keep the first value seen
    - ``"last"``   – keep the last value seen
    """
    if on_conflict not in ("error", "first", "last"):
        raise ValueError(f"Invalid on_conflict value: {on_conflict!r}")

    result: Dict[str, str] = {}
    for raw_key, raw_value in env.items():
        nk = normalize_key(raw_key, upper=upper, replace_hyphens=replace_hyphens)
        nv = normalize_value(raw_value, strip=strip_values, collapse_whitespace=collapse_whitespace)
        if nk in result:
            if on_conflict == "error":
                raise NormalizeError(
                    f"Normalization conflict: multiple keys map to {nk!r}."
                )
            elif on_conflict == "first":
                continue  # keep existing
            # on_conflict == "last": fall through to overwrite
        result[nk] = nv
    return result
