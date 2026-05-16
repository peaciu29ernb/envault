"""Flatten nested dict structures into dot-notation env keys and expand them back."""

from typing import Any


class FlattenError(Exception):
    """Raised when flattening or expanding fails."""


def flatten_dict(
    data: dict,
    prefix: str = "",
    separator: str = "__",
) -> dict[str, str]:
    """Recursively flatten a nested dict into a flat env-style dict.

    Example::

        {"db": {"host": "localhost", "port": "5432"}}
        -> {"DB__HOST": "localhost", "DB__PORT": "5432"}
    """
    result: dict[str, str] = {}
    for key, value in data.items():
        if not isinstance(key, str):
            raise FlattenError(f"All keys must be strings; got {type(key)!r}")
        full_key = f"{prefix}{separator}{key}" if prefix else key
        full_key = full_key.upper()
        if isinstance(value, dict):
            nested = flatten_dict(value, prefix=full_key, separator=separator)
            result.update(nested)
        elif isinstance(value, (str, int, float, bool)) or value is None:
            result[full_key] = "" if value is None else str(value)
        else:
            raise FlattenError(
                f"Unsupported value type {type(value)!r} for key '{full_key}'"
            )
    return result


def expand_dict(
    env: dict[str, str],
    separator: str = "__",
) -> dict[str, Any]:
    """Expand a flat env dict back into a nested dict structure.

    Example::

        {"DB__HOST": "localhost", "DB__PORT": "5432"}
        -> {"DB": {"HOST": "localhost", "PORT": "5432"}}
    """
    result: dict[str, Any] = {}
    for key, value in env.items():
        parts = key.split(separator)
        node = result
        for part in parts[:-1]:
            if part not in node:
                node[part] = {}
            elif not isinstance(node[part], dict):
                raise FlattenError(
                    f"Key conflict at '{part}': expected dict, got scalar"
                )
            node = node[part]
        leaf = parts[-1]
        if leaf in node and isinstance(node[leaf], dict):
            raise FlattenError(
                f"Key conflict at '{leaf}': expected scalar, got dict"
            )
        node[leaf] = value
    return result


def flatten_env(env: dict[str, str], separator: str = "__") -> dict[str, str]:
    """Convenience wrapper: flatten an already-flat env (no-op for flat dicts)."""
    return flatten_dict(env, separator=separator)
