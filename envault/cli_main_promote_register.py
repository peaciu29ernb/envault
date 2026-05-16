"""Registration helper — attaches the promote command group to the root CLI.

Import this module in envault/cli.py to activate the ``envault promote`` sub-command::

    from envault.cli_main_promote_register import register_promote
    register_promote(cli)
"""

from __future__ import annotations

import click

from envault.cli_promote import promote_cmd


def register_promote(root: click.Group) -> None:
    """Attach the *promote* command group to *root*."""
    root.add_command(promote_cmd)
