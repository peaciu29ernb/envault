"""Sort environment variable dictionaries by various criteria."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional


class SortError(Exception):
    """Raised when a sort operation cannot be completed."""


def sort_alphabetical(env: Dict[str, str], *, reverse: bool = False) -> Dict[str, str]:
    """Return a new dict sorted alphabetically by key."""
    return dict(sorted(env.items(), key=lambda kv: kv[0], reverse=reverse))


def sort_by_value_length(env: Dict[str, str], *, reverse: bool = False) -> Dict[str, str]:
    """Return a new dict sorted by the length of each value."""
    return dict(sorted(env.items(), key=lambda kv: len(kv[1]), reverse=reverse))


def sort_by_key_length(env: Dict[str, str], *, reverse: bool = False) -> Dict[str, str]:
    """Return a new dict sorted by the length of each key."""
    return dict(sorted(env.items(), key=lambda kv: len(kv[0]), reverse=reverse))


def sort_by_custom(env: Dict[str, str], order: List[str], *, remainder_last: bool = True) -> Dict[str, str]:
    """Return a new dict ordered by an explicit key list.

    Keys not in *order* are appended at the end (or beginning if
    ``remainder_last=False``).

    Raises :class:`SortError` if *order* contains duplicate entries.
    """
    if len(order) != len(set(order)):
        raise SortError("order list contains duplicate keys")

    ordered: Dict[str, str] = {}
    remainder: Dict[str, str] = {}

    order_index = {k: i for i, k in enumerate(order)}
    for key, value in env.items():
        if key in order_index:
            ordered[key] = value
        else:
            remainder[key] = value

    # Sort the matched keys by their position in *order*
    sorted_ordered = dict(sorted(ordered.items(), key=lambda kv: order_index[kv[0]]))

    if remainder_last:
        return {**sorted_ordered, **remainder}
    return {**remainder, **sorted_ordered}


def sort_env(
    env: Dict[str, str],
    strategy: str = "alpha",
    *,
    reverse: bool = False,
    order: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Dispatch to a sort strategy by name.

    Supported strategies: ``alpha``, ``key_length``, ``value_length``, ``custom``.
    """
    strategies = {
        "alpha": lambda: sort_alphabetical(env, reverse=reverse),
        "key_length": lambda: sort_by_key_length(env, reverse=reverse),
        "value_length": lambda: sort_by_value_length(env, reverse=reverse),
        "custom": lambda: sort_by_custom(env, order or [], remainder_last=not reverse),
    }
    if strategy not in strategies:
        raise SortError(
            f"unknown strategy '{strategy}'; choose from: {', '.join(strategies)}"
        )
    return strategies[strategy]()
