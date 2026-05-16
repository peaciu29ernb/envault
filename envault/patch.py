"""envault.patch — Apply partial updates (patches) to a decrypted env dict.

Supports set, delete, and rename operations in a single atomic patch.
"""

from __future__ import annotations

from typing import Any


class PatchError(Exception):
    """Raised when a patch operation is invalid or cannot be applied."""


# ---------------------------------------------------------------------------
# Core patch operations
# ---------------------------------------------------------------------------

def apply_patch(env: dict[str, str], patch: list[dict[str, Any]]) -> dict[str, str]:
    """Return a *new* env dict with all patch operations applied in order.

    Each operation is a dict with at minimum an ``"op"`` key:

    * ``{"op": "set",    "key": "FOO", "value": "bar"}``
    * ``{"op": "delete", "key": "FOO"}``
    * ``{"op": "rename", "from": "OLD", "to": "NEW"}``

    Raises :class:`PatchError` on unknown ops or missing required fields.
    """
    result = dict(env)
    for i, op in enumerate(patch):
        kind = op.get("op")
        if kind == "set":
            _require(op, "key", "value", index=i)
            result[op["key"]] = op["value"]
        elif kind == "delete":
            _require(op, "key", index=i)
            if op["key"] not in result:
                raise PatchError(
                    f"Patch op #{i}: delete — key '{op['key']}' not found."
                )
            del result[op["key"]]
        elif kind == "rename":
            _require(op, "from", "to", index=i)
            src, dst = op["from"], op["to"]
            if src not in result:
                raise PatchError(
                    f"Patch op #{i}: rename — source key '{src}' not found."
                )
            if dst in result:
                raise PatchError(
                    f"Patch op #{i}: rename — destination key '{dst}' already exists."
                )
            result[dst] = result.pop(src)
        else:
            raise PatchError(
                f"Patch op #{i}: unknown operation '{kind}'. "
                "Expected 'set', 'delete', or 'rename'."
            )
    return result


def build_patch(
    before: dict[str, str],
    after: dict[str, str],
) -> list[dict[str, Any]]:
    """Derive the minimal list of patch operations that transforms *before* into *after*.

    Only ``set`` and ``delete`` ops are emitted (rename detection is not attempted).
    """
    ops: list[dict[str, Any]] = []
    for key, value in after.items():
        if before.get(key) != value:
            ops.append({"op": "set", "key": key, "value": value})
    for key in before:
        if key not in after:
            ops.append({"op": "delete", "key": key})
    return ops


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _require(op: dict[str, Any], *fields: str, index: int) -> None:
    for field in fields:
        if field not in op:
            raise PatchError(
                f"Patch op #{index} ('{op.get('op')}'): missing required field '{field}'."
            )
