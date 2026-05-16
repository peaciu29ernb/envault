"""sanitize.py — Strip, normalize, and clean env variable values."""

import re
from typing import Dict, List, Optional


class SanitizeError(Exception):
    """Raised when a sanitization rule cannot be applied."""


# Supported sanitizers
_SANITIZERS = {
    "strip": str.strip,
    "lower": str.lower,
    "upper": str.upper,
    "strip_quotes": lambda v: v.strip("'\"" ),
    "collapse_whitespace": lambda v: re.sub(r"\s+", " ", v).strip(),
    "remove_newlines": lambda v: v.replace("\n", "").replace("\r", ""),
    "remove_non_printable": lambda v: re.sub(r"[^\x20-\x7E]", "", v),
    "truncate_512": lambda v: v[:512],
}


def list_sanitizers() -> List[str]:
    """Return the names of all available sanitizers."""
    return list(_SANITIZERS.keys())


def apply_sanitizer(value: str, name: str) -> str:
    """Apply a single named sanitizer to *value*.

    Raises SanitizeError if the sanitizer name is unknown.
    """
    if name not in _SANITIZERS:
        raise SanitizeError(
            f"Unknown sanitizer {name!r}. Available: {list_sanitizers()}"
        )
    return _SANITIZERS[name](value)


def apply_sanitizers(value: str, names: List[str]) -> str:
    """Apply a sequence of sanitizers to *value* in order."""
    for name in names:
        value = apply_sanitizer(value, name)
    return value


def sanitize_env(
    env: Dict[str, str],
    sanitizers: List[str],
    keys: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Return a new env dict with *sanitizers* applied to each value.

    If *keys* is provided only those keys are sanitized; all others are
    copied unchanged.
    """
    result: Dict[str, str] = {}
    for k, v in env.items():
        if keys is None or k in keys:
            result[k] = apply_sanitizers(v, sanitizers)
        else:
            result[k] = v
    return result
