"""cascade.py — Resolve env variables by cascading through multiple sources.

Sources are evaluated in order; the first source that defines a key wins
(unless override=True, in which case later sources overwrite earlier ones).
"""

from typing import Dict, List, Optional, Tuple


CascadeSource = Dict[str, str]


def cascade_envs(
    sources: List[CascadeSource],
    *,
    override: bool = False,
) -> Dict[str, str]:
    """Merge multiple env dicts in cascade order.

    Args:
        sources: List of env dicts ordered from lowest to highest priority
                 (index 0 is base, last index is most specific).
        override: If False (default), first definition wins.  If True, later
                  sources overwrite earlier ones (last wins).

    Returns:
        Merged dict.
    """
    result: Dict[str, str] = {}
    if override:
        for source in sources:
            result.update(source)
    else:
        for source in sources:
            for key, value in source.items():
                if key not in result:
                    result[key] = value
    return result


def cascade_with_origins(
    sources: List[Tuple[str, CascadeSource]],
    *,
    override: bool = False,
) -> Dict[str, Tuple[str, str]]:
    """Like cascade_envs but also tracks which source each key came from.

    Args:
        sources: List of (label, env_dict) tuples.
        override: Same semantics as cascade_envs.

    Returns:
        Dict mapping key -> (source_label, value).
    """
    result: Dict[str, Tuple[str, str]] = {}
    if override:
        for label, env in sources:
            for key, value in env.items():
                result[key] = (label, value)
    else:
        for label, env in sources:
            for key, value in env.items():
                if key not in result:
                    result[key] = (label, value)
    return result


def list_conflicts(
    sources: List[Tuple[str, CascadeSource]],
) -> Dict[str, List[Tuple[str, str]]]:
    """Return keys defined in more than one source with differing values.

    Returns:
        Dict mapping conflicting key -> list of (source_label, value) pairs.
    """
    seen: Dict[str, List[Tuple[str, str]]] = {}
    for label, env in sources:
        for key, value in env.items():
            seen.setdefault(key, []).append((label, value))

    conflicts = {}
    for key, entries in seen.items():
        values = [v for _, v in entries]
        if len(set(values)) > 1:
            conflicts[key] = entries
    return conflicts


def effective_value(
    key: str,
    sources: List[Tuple[str, CascadeSource]],
    *,
    override: bool = False,
) -> Optional[Tuple[str, str]]:
    """Return (source_label, value) for *key* using cascade semantics, or None."""
    origins = cascade_with_origins(sources, override=override)
    return origins.get(key)
