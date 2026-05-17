"""Clone / copy an env dict with optional key filtering and transformation."""

from __future__ import annotations

from typing import Callable, Container, Dict, Iterable, Optional


class CloneError(Exception):
    """Raised when a clone operation cannot be completed."""


def clone_env(
    env: Dict[str, str],
    *,
    include: Optional[Iterable[str]] = None,
    exclude: Optional[Container[str]] = None,
    prefix: Optional[str] = None,
    strip_prefix: bool = False,
    transform: Optional[Callable[[str, str], tuple[str, str]]] = None,
) -> Dict[str, str]:
    """Return a (shallow) copy of *env* with optional filtering.

    Parameters
    ----------
    include:
        Explicit allow-list of keys to copy.  When *None* all keys are
        considered (subject to *exclude* and *prefix*).
    exclude:
        Keys to drop from the result.  Applied after *include* / *prefix*.
    prefix:
        Only copy keys that start with this string.
    strip_prefix:
        When *True* and *prefix* is set, remove the prefix from the copied
        key names.
    transform:
        Optional callable ``(key, value) -> (new_key, new_value)`` applied
        to every surviving pair before insertion into the result.
    """
    if include is not None:
        items = [(k, env[k]) for k in include if k in env]
    else:
        items = list(env.items())

    if prefix is not None:
        items = [(k, v) for k, v in items if k.startswith(prefix)]
        if strip_prefix:
            items = [(k[len(prefix):], v) for k, v in items]

    if exclude is not None:
        items = [(k, v) for k, v in items if k not in exclude]

    if transform is not None:
        items = [transform(k, v) for k, v in items]

    # Detect duplicate keys that may arise after prefix stripping / transform
    result: Dict[str, str] = {}
    for k, v in items:
        if not isinstance(k, str) or not isinstance(v, str):
            raise CloneError(
                f"transform must return (str, str); got ({type(k).__name__}, {type(v).__name__})"
            )
        if k in result:
            raise CloneError(f"Duplicate key '{k}' produced during clone.")
        result[k] = v

    return result


def clone_report(original: Dict[str, str], cloned: Dict[str, str]) -> Dict[str, object]:
    """Return a summary dict describing what was kept / dropped."""
    original_keys = set(original.keys())
    cloned_keys = set(cloned.keys())
    return {
        "original_count": len(original_keys),
        "cloned_count": len(cloned_keys),
        "dropped": sorted(original_keys - cloned_keys),
        "renamed": sorted(cloned_keys - original_keys),
    }
