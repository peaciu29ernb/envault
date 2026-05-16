"""resolve.py — Resolve the final effective value of a key across
multiple sources (vault, profiles, overrides, defaults)."""

from __future__ import annotations

from typing import Any


class ResolveResult:
    """Holds the resolved value and metadata about where it came from."""

    def __init__(self, key: str, value: str | None, source: str | None, resolved: bool):
        self.key = key
        self.value = value
        self.source = source
        self.resolved = resolved

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ResolveResult(key={self.key!r}, value={self.value!r}, "
            f"source={self.source!r}, resolved={self.resolved})"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "source": self.source,
            "resolved": self.resolved,
        }


def resolve_key(
    key: str,
    sources: list[tuple[str, dict[str, str]]],
    default: str | None = None,
) -> ResolveResult:
    """Resolve *key* from an ordered list of (source_name, env_dict) pairs.

    The first source that contains *key* wins.  If no source provides the
    key and *default* is given, the result carries source='default'.
    """
    for source_name, env in sources:
        if key in env:
            return ResolveResult(key=key, value=env[key], source=source_name, resolved=True)

    if default is not None:
        return ResolveResult(key=key, value=default, source="default", resolved=True)

    return ResolveResult(key=key, value=None, source=None, resolved=False)


def resolve_all(
    keys: list[str],
    sources: list[tuple[str, dict[str, str]]],
    defaults: dict[str, str] | None = None,
) -> dict[str, ResolveResult]:
    """Resolve every key in *keys* across *sources*.

    *defaults* is an optional mapping of key → fallback value.
    """
    defaults = defaults or {}
    return {
        key: resolve_key(key, sources, default=defaults.get(key))
        for key in keys
    }


def unresolved_keys(
    results: dict[str, ResolveResult],
) -> list[str]:
    """Return keys that could not be resolved in *results*."""
    return [key for key, result in results.items() if not result.resolved]
