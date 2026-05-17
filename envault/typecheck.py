"""Type-checking utilities for env var values."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


class TypeCheckError(Exception):
    """Raised when a type check fails and strict mode is on."""


_BOOL_TRUTHY = {"true", "1", "yes", "on"}
_BOOL_FALSY = {"false", "0", "no", "off"}


def is_int(value: str) -> bool:
    """Return True if value represents a valid integer."""
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False


def is_float(value: str) -> bool:
    """Return True if value represents a valid float."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def is_bool(value: str) -> bool:
    """Return True if value is a recognisable boolean string."""
    return value.strip().lower() in _BOOL_TRUTHY | _BOOL_FALSY


def is_url(value: str) -> bool:
    """Return True if value looks like an http/https/ftp URL."""
    return bool(re.match(r"^(https?|ftp)://", value.strip(), re.IGNORECASE))


def is_email(value: str) -> bool:
    """Return True if value looks like an e-mail address."""
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value.strip()))


def infer_type(value: str) -> str:
    """Infer the most specific type name for *value*."""
    if is_bool(value):
        return "bool"
    if is_int(value):
        return "int"
    if is_float(value):
        return "float"
    if is_url(value):
        return "url"
    if is_email(value):
        return "email"
    return "str"


def typecheck_env(
    env: Dict[str, str],
    schema: Dict[str, str],
    *,
    strict: bool = False,
) -> List[Dict[str, Any]]:
    """Validate *env* values against a *schema* mapping key -> expected type.

    Returns a list of violation dicts.  Raises :class:`TypeCheckError` on the
    first violation when *strict* is ``True``.
    """
    violations: List[Dict[str, Any]] = []
    checkers = {
        "int": is_int,
        "float": is_float,
        "bool": is_bool,
        "url": is_url,
        "email": is_email,
        "str": lambda _v: True,
    }
    for key, expected in schema.items():
        if key not in env:
            continue
        checker = checkers.get(expected)
        if checker is None:
            continue
        if not checker(env[key]):
            violation = {
                "key": key,
                "expected": expected,
                "actual_value": env[key],
                "inferred": infer_type(env[key]),
            }
            if strict:
                raise TypeCheckError(
                    f"{key}: expected {expected}, got {violation['inferred']!r}"
                )
            violations.append(violation)
    return violations
