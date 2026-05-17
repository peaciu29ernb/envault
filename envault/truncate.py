"""Truncate long env values to a maximum length, with optional suffix."""

from __future__ import annotations

__all__ = [
    "TruncateError",
    "truncate_value",
    "truncate_env",
    "truncate_report",
]


class TruncateError(Exception):
    """Raised when truncation parameters are invalid."""


def truncate_value(
    value: str,
    max_length: int,
    suffix: str = "...",
    strict: bool = False,
) -> str:
    """Return *value* truncated to *max_length* characters.

    If *value* already fits, it is returned unchanged.  When truncation is
    needed the returned string ends with *suffix* and its total length does
    not exceed *max_length*.  If *max_length* is shorter than *suffix* a
    ``TruncateError`` is raised unless *strict* is ``False``, in which case
    the raw slice is returned without a suffix.
    """
    if max_length < 0:
        raise TruncateError("max_length must be >= 0")
    if len(value) <= max_length:
        return value
    if len(suffix) >= max_length:
        if strict:
            raise TruncateError(
                f"max_length ({max_length}) is too short to accommodate suffix ({suffix!r})"
            )
        return value[:max_length]
    return value[: max_length - len(suffix)] + suffix


def truncate_env(
    env: dict[str, str],
    max_length: int,
    suffix: str = "...",
    keys: list[str] | None = None,
) -> dict[str, str]:
    """Return a new env dict with values truncated to *max_length*.

    If *keys* is provided only those keys are considered; all others are
    copied verbatim.
    """
    result: dict[str, str] = {}
    for k, v in env.items():
        if keys is None or k in keys:
            result[k] = truncate_value(v, max_length, suffix=suffix)
        else:
            result[k] = v
    return result


def truncate_report(env: dict[str, str], max_length: int) -> list[dict]:
    """Return a list of dicts describing keys whose values exceed *max_length*.

    Each entry has ``key``, ``original_length``, and ``truncated_length``.
    """
    report: list[dict] = []
    for k, v in env.items():
        if len(v) > max_length:
            report.append(
                {
                    "key": k,
                    "original_length": len(v),
                    "truncated_length": max_length,
                }
            )
    return report
