"""envault.coerce — Type coercion utilities for env var values.

Provides functions to coerce string env values to native Python types
(bool, int, float, list) and to coerce an entire env dict at once using
a schema that maps key names to target types.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

__all__ = [
    "CoerceError",
    "coerce_bool",
    "coerce_int",
    "coerce_float",
    "coerce_list",
    "coerce_value",
    "coerce_env",
]

_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


class CoerceError(ValueError):
    """Raised when a value cannot be coerced to the requested type."""


def coerce_bool(value: str) -> bool:
    """Coerce a string to bool.  Raises CoerceError on unrecognised values."""
    normalised = value.strip().lower()
    if normalised in _TRUE_VALUES:
        return True
    if normalised in _FALSE_VALUES:
        return False
    raise CoerceError(
        f"Cannot coerce {value!r} to bool. "
        f"Expected one of: {sorted(_TRUE_VALUES | _FALSE_VALUES)}"
    )


def coerce_int(value: str) -> int:
    """Coerce a string to int.  Raises CoerceError on failure."""
    try:
        return int(value.strip())
    except ValueError:
        raise CoerceError(f"Cannot coerce {value!r} to int.")


def coerce_float(value: str) -> float:
    """Coerce a string to float.  Raises CoerceError on failure."""
    try:
        return float(value.strip())
    except ValueError:
        raise CoerceError(f"Cannot coerce {value!r} to float.")


def coerce_list(value: str, delimiter: str = ",") -> List[str]:
    """Split a delimited string into a list of stripped, non-empty strings."""
    return [item.strip() for item in value.split(delimiter) if item.strip()]


_COERCERS = {
    "bool": coerce_bool,
    "int": coerce_int,
    "float": coerce_float,
    "list": coerce_list,
    "str": str,
}


def coerce_value(value: str, type_name: str) -> Any:
    """Coerce *value* to the type identified by *type_name*.

    Supported type names: ``'str'``, ``'bool'``, ``'int'``, ``'float'``,
    ``'list'``.
    """
    if type_name not in _COERCERS:
        raise CoerceError(
            f"Unknown type {type_name!r}. Supported: {sorted(_COERCERS)}"
        )
    return _COERCERS[type_name](value)


def coerce_env(
    env: Dict[str, str],
    schema: Dict[str, str],
    *,
    strict: bool = False,
) -> Dict[str, Any]:
    """Return a new dict with values coerced according to *schema*.

    Keys absent from *schema* are passed through as plain strings.
    If *strict* is True, a CoerceError is raised for any key in *schema*
    that is missing from *env*.
    """
    result: Dict[str, Any] = {}
    for key, raw in env.items():
        if key in schema:
            result[key] = coerce_value(raw, schema[key])
        else:
            result[key] = raw
    if strict:
        missing = set(schema) - set(env)
        if missing:
            raise CoerceError(
                f"Keys required by schema but missing from env: {sorted(missing)}"
            )
    return result
