"""Merge utilities for combining .env variable sets with conflict resolution."""

from typing import Dict, Optional, Tuple

MergeStrategy = str
STRATEGY_OURS = "ours"
STRATEGY_THEIRS = "theirs"
STRATEGY_PROMPT = "prompt"


def merge_envs(
    base: Dict[str, str],
    incoming: Dict[str, str],
    strategy: MergeStrategy = STRATEGY_OURS,
) -> Tuple[Dict[str, str], Dict[str, list]]:
    """Merge two env dicts, returning merged result and a conflict report.

    Args:
        base: The existing/current env variables.
        incoming: The new env variables to merge in.
        strategy: How to resolve conflicts — 'ours' keeps base value,
                  'theirs' takes incoming value.

    Returns:
        A tuple of (merged_dict, conflict_report) where conflict_report maps
        conflicting keys to [base_value, incoming_value].
    """
    if strategy not in (STRATEGY_OURS, STRATEGY_THEIRS):
        raise ValueError(
            f"Unsupported merge strategy '{strategy}'. "
            f"Use '{STRATEGY_OURS}' or '{STRATEGY_THEIRS}'."
        )

    merged: Dict[str, str] = {**base}
    conflicts: Dict[str, list] = {}

    for key, incoming_val in incoming.items():
        if key not in base:
            # New key — always add
            merged[key] = incoming_val
        elif base[key] != incoming_val:
            # Conflict detected
            conflicts[key] = [base[key], incoming_val]
            if strategy == STRATEGY_THEIRS:
                merged[key] = incoming_val
            # STRATEGY_OURS: keep base value (already in merged)

    return merged, conflicts


def format_merge_report(
    conflicts: Dict[str, list],
    strategy: MergeStrategy = STRATEGY_OURS,
) -> str:
    """Return a human-readable string summarising merge conflicts."""
    if not conflicts:
        return "No conflicts. Merge completed cleanly."

    lines = [f"Merge conflicts resolved using strategy='{strategy}':", ""]
    for key, (base_val, incoming_val) in conflicts.items():
        kept = base_val if strategy == STRATEGY_OURS else incoming_val
        discarded = incoming_val if strategy == STRATEGY_OURS else base_val
        lines.append(f"  {key}:")
        lines.append(f"    kept     : {kept}")
        lines.append(f"    discarded: {discarded}")
    return "\n".join(lines)
