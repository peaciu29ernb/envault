"""Deduplication utilities for env variable keys across multiple sources."""

from typing import Dict, List, Optional, Tuple


class DedupError(Exception):
    """Raised when deduplication encounters an unrecoverable problem."""


def find_duplicate_keys(*envs: Dict[str, str]) -> Dict[str, List[int]]:
    """Return a mapping of key -> list of source indices where the key appears.

    Only keys present in more than one source are included.
    """
    occurrences: Dict[str, List[int]] = {}
    for idx, env in enumerate(envs):
        for key in env:
            occurrences.setdefault(key, []).append(idx)
    return {k: v for k, v in occurrences.items() if len(v) > 1}


def dedup_keys(
    *envs: Dict[str, str],
    strategy: str = "first",
) -> Dict[str, str]:
    """Merge multiple env dicts, resolving duplicate keys by *strategy*.

    Strategies:
        ``first``  – keep the value from the earliest source (default).
        ``last``   – keep the value from the latest source.
        ``error``  – raise :class:`DedupError` if any duplicate key is found.

    :param envs: Two or more env dicts to merge.
    :param strategy: Conflict-resolution strategy.
    :returns: A single merged env dict.
    :raises DedupError: When *strategy* is ``"error"`` and duplicates exist.
    """
    if strategy not in ("first", "last", "error"):
        raise ValueError(f"Unknown dedup strategy: {strategy!r}")

    if strategy == "error":
        dupes = find_duplicate_keys(*envs)
        if dupes:
            keys = ", ".join(sorted(dupes))
            raise DedupError(f"Duplicate keys found across sources: {keys}")

    result: Dict[str, str] = {}
    sources = list(envs) if strategy == "first" else list(reversed(envs))
    for env in sources:
        for k, v in env.items():
            if k not in result:
                result[k] = v
    return result


def dedup_report(
    *envs: Dict[str, str],
) -> List[Tuple[str, Dict[int, str]]]:
    """Return a human-readable report of all duplicate keys and their values.

    Each entry is ``(key, {source_index: value, ...})``.
    """
    dupes = find_duplicate_keys(*envs)
    report: List[Tuple[str, Dict[int, str]]] = []
    for key in sorted(dupes):
        values_by_source = {
            idx: envs[idx][key]
            for idx in dupes[key]
        }
        report.append((key, values_by_source))
    return report
