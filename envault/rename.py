"""Key rename/move utility for envault.

Provides functions to rename keys within a decrypted env dict,
with optional conflict handling and audit trail support.
"""

from typing import Dict, Optional


class RenameError(Exception):
    """Raised when a rename operation cannot be completed."""


def rename_key(
    env: Dict[str, str],
    old_key: str,
    new_key: str,
    overwrite: bool = False,
) -> Dict[str, str]:
    """Return a new env dict with *old_key* renamed to *new_key*.

    Parameters
    ----------
    env:       Source environment dictionary.
    old_key:   Key to rename.
    new_key:   Target key name.
    overwrite: If True, silently replace an existing *new_key*.
               If False (default), raise RenameError on collision.

    Returns
    -------
    A new dict — the original is never mutated.
    """
    if old_key not in env:
        raise RenameError(f"Key '{old_key}' not found in environment.")
    if old_key == new_key:
        return dict(env)
    if new_key in env and not overwrite:
        raise RenameError(
            f"Key '{new_key}' already exists. Use overwrite=True to replace it."
        )
    result = {}
    for k, v in env.items():
        if k == old_key:
            result[new_key] = v
        elif k != new_key:  # drop old new_key when overwriting
            result[k] = v
        # if overwrite and k == new_key: skip the old value
    return result


def rename_bulk(
    env: Dict[str, str],
    mapping: Dict[str, str],
    overwrite: bool = False,
) -> Dict[str, str]:
    """Apply multiple renames described by *mapping* {old: new}.

    Renames are applied sequentially in insertion order.  If any
    single rename fails the whole operation is aborted and the
    original dict is returned unchanged.
    """
    result = dict(env)
    for old, new in mapping.items():
        result = rename_key(result, old, new, overwrite=overwrite)
    return result


def rename_by_prefix(
    env: Dict[str, str],
    old_prefix: str,
    new_prefix: str,
    overwrite: bool = False,
) -> Dict[str, str]:
    """Rename all keys whose name starts with *old_prefix*."""
    mapping = {
        k: new_prefix + k[len(old_prefix):]
        for k in env
        if k.startswith(old_prefix)
    }
    if not mapping:
        raise RenameError(f"No keys found with prefix '{old_prefix}'.")
    return rename_bulk(env, mapping, overwrite=overwrite)
