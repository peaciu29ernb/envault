"""Register the typecheck command group with the main CLI."""
from __future__ import annotations

from envault.cli import cli
from envault.cli_typecheck import typecheck_cmd


def register_typecheck() -> None:
    """Attach the *typecheck* sub-command group to the root CLI."""
    cli.add_command(typecheck_cmd)
