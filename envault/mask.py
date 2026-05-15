"""Masking utilities for displaying env values safely in output."""

from typing import Dict, Optional

_DEFAULT_MASK = "****"
_DEFAULT_VISIBLE_CHARS = 4


def mask_value(
    value: str,
    visible_chars: int = _DEFAULT_VISIBLE_CHARS,
    mask: str = _DEFAULT_MASK,
    show_suffix: bool = False,
) -> str:
    """Mask a value, optionally showing a prefix or suffix of visible characters."""
    if not value:
        return mask
    if len(value) <= visible_chars:
        return mask
    if show_suffix:
        return mask + value[-visible_chars:]
    return value[:visible_chars] + mask


def mask_env(
    env: Dict[str, str],
    keys: Optional[list] = None,
    visible_chars: int = _DEFAULT_VISIBLE_CHARS,
    mask: str = _DEFAULT_MASK,
    show_suffix: bool = False,
) -> Dict[str, str]:
    """Return a copy of env dict with specified (or all) values masked."""
    result = {}
    for k, v in env.items():
        if keys is None or k in keys:
            result[k] = mask_value(v, visible_chars=visible_chars, mask=mask, show_suffix=show_suffix)
        else:
            result[k] = v
    return result


def unmask_value(masked: str, original: str) -> str:
    """Return the original value (identity helper for symmetry in pipelines)."""
    return original


def format_masked_env(
    env: Dict[str, str],
    keys: Optional[list] = None,
    visible_chars: int = _DEFAULT_VISIBLE_CHARS,
    mask: str = _DEFAULT_MASK,
    show_suffix: bool = False,
) -> str:
    """Return a human-readable string of the env with selected keys masked."""
    masked = mask_env(env, keys=keys, visible_chars=visible_chars, mask=mask, show_suffix=show_suffix)
    lines = [f"{k}={v}" for k, v in sorted(masked.items())]
    return "\n".join(lines)
