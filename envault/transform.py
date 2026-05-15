"""Value transformation utilities for env variables."""

import re
from typing import Callable, Dict, List, Optional


class TransformError(Exception):
    pass


_BUILTIN_TRANSFORMS: Dict[str, Callable[[str], str]] = {
    "upper": str.upper,
    "lower": str.lower,
    "strip": str.strip,
    "base64_encode": lambda v: __import__("base64").b64encode(v.encode()).decode(),
    "base64_decode": lambda v: __import__("base64").b64decode(v.encode()).decode(),
    "url_encode": lambda v: __import__("urllib.parse", fromlist=["quote"]).quote(v, safe=""),
    "trim_quotes": lambda v: v.strip("'\"\t "),
}


def apply_transform(value: str, transform_name: str) -> str:
    """Apply a named transform to a single value."""
    if transform_name not in _BUILTIN_TRANSFORMS:
        raise TransformError(f"Unknown transform: '{transform_name}'")
    try:
        return _BUILTIN_TRANSFORMS[transform_name](value)
    except Exception as exc:
        raise TransformError(f"Transform '{transform_name}' failed: {exc}") from exc


def apply_transforms(value: str, transforms: List[str]) -> str:
    """Apply a pipeline of transforms to a value in order."""
    result = value
    for t in transforms:
        result = apply_transform(result, t)
    return result


def transform_env(
    env: Dict[str, str],
    rules: Dict[str, List[str]],
    *,
    skip_missing: bool = True,
) -> Dict[str, str]:
    """Apply transform pipelines to matching keys in an env dict.

    Args:
        env: The source env dict.
        rules: Mapping of key (or glob pattern) to list of transform names.
        skip_missing: If True, keys in rules not present in env are silently skipped.

    Returns:
        A new dict with transformed values.
    """
    import fnmatch

    result = dict(env)
    for pattern, transforms in rules.items():
        matched = [
            k for k in env if fnmatch.fnmatchcase(k, pattern)
        ]
        if not matched and not skip_missing:
            raise TransformError(f"No keys matched pattern: '{pattern}'")
        for key in matched:
            result[key] = apply_transforms(env[key], transforms)
    return result


def list_transforms() -> List[str]:
    """Return names of all available built-in transforms."""
    return sorted(_BUILTIN_TRANSFORMS.keys())
