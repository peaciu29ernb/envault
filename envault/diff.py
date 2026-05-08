"""Utilities for comparing two .env variable sets and reporting differences."""

from typing import Dict, List, Tuple


EnvDict = Dict[str, str]


def diff_envs(old: EnvDict, new: EnvDict) -> Dict[str, List[Tuple[str, str]]]:
    """Compare two env dicts and return a structured diff.

    Returns a dict with keys:
      - 'added':   list of (key, new_value)
      - 'removed': list of (key, old_value)
      - 'changed': list of (key, old_value, new_value)
      - 'unchanged': list of (key, value)
    """
    old_keys = set(old.keys())
    new_keys = set(new.keys())

    added = [(k, new[k]) for k in sorted(new_keys - old_keys)]
    removed = [(k, old[k]) for k in sorted(old_keys - new_keys)]
    changed = [
        (k, old[k], new[k])
        for k in sorted(old_keys & new_keys)
        if old[k] != new[k]
    ]
    unchanged = [
        (k, old[k])
        for k in sorted(old_keys & new_keys)
        if old[k] == new[k]
    ]

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
    }


def format_diff(diff: Dict[str, list], show_values: bool = False) -> str:
    """Format a diff dict as a human-readable string.

    Args:
        diff: Output from diff_envs().
        show_values: If True, include values in the output.

    Returns:
        Multi-line string summarising the diff.
    """
    lines = []

    for key, value in diff["added"]:
        val_part = f" = {value!r}" if show_values else ""
        lines.append(f"+ {key}{val_part}")

    for key, value in diff["removed"]:
        val_part = f" = {value!r}" if show_values else ""
        lines.append(f"- {key}{val_part}")

    for key, old_val, new_val in diff["changed"]:
        if show_values:
            lines.append(f"~ {key}: {old_val!r} -> {new_val!r}")
        else:
            lines.append(f"~ {key}")

    for key, _ in diff["unchanged"]:
        lines.append(f"  {key}")

    return "\n".join(lines)


def has_changes(diff: Dict[str, list]) -> bool:
    """Return True if there are any added, removed, or changed keys."""
    return bool(diff["added"] or diff["removed"] or diff["changed"])
