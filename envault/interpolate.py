"""interpolate.py – resolve variable references within an env dict.

Supports ${VAR} and $VAR style self-references so that values like
  BASE_URL=https://example.com
  API_URL=${BASE_URL}/api
are expanded to their final form.
"""

from __future__ import annotations

import re
from typing import Dict, Optional

_BRACED = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
_BARE = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)")


class InterpolateError(Exception):
    """Raised when interpolation cannot be completed."""


def _expand_value(
    value: str,
    env: Dict[str, str],
    visiting: set,
    key: str,
    strict: bool,
) -> str:
    """Recursively expand variable references in *value*."""

    def _replace(match: re.Match, bare: bool = False) -> str:
        ref = match.group(1)
        if ref in visiting:
            raise InterpolateError(
                f"Circular reference detected: {key!r} -> {ref!r}"
            )
        if ref not in env:
            if strict:
                raise InterpolateError(
                    f"Undefined variable {ref!r} referenced in key {key!r}"
                )
            return match.group(0)  # leave unexpanded
        visiting.add(ref)
        result = _expand_value(env[ref], env, visiting, ref, strict)
        visiting.discard(ref)
        return result

    value = _BRACED.sub(lambda m: _replace(m), value)
    value = _BARE.sub(lambda m: _replace(m, bare=True), value)
    return value


def interpolate_env(
    env: Dict[str, str],
    strict: bool = False,
    skip_keys: Optional[list] = None,
) -> Dict[str, str]:
    """Return a new dict with all variable references expanded.

    Args:
        env:       Source env mapping.
        strict:    If True, raise InterpolateError for undefined references.
        skip_keys: Keys whose values should be left unchanged.

    Returns:
        New dict with interpolated values.
    """
    skip = set(skip_keys or [])
    result: Dict[str, str] = {}
    for key, value in env.items():
        if key in skip:
            result[key] = value
        else:
            result[key] = _expand_value(value, env, {key}, key, strict)
    return result


def find_references(env: Dict[str, str]) -> Dict[str, list]:
    """Return a mapping of key -> list of variable names it references."""
    refs: Dict[str, list] = {}
    for key, value in env.items():
        found = _BRACED.findall(value) + _BARE.findall(value)
        if found:
            refs[key] = list(dict.fromkeys(found))  # deduplicated, ordered
    return refs
