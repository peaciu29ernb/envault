"""CLI commands for pinning/unpinning env keys."""

from __future__ import annotations

import click
from envault.pin import pin_key, unpin_key, get_pins, clear_pins, is_pinned


@click.group(name="pin")
def pin_cmd():
    """Manage pinned keys (excluded from rotation)."""


@pin_cmd.command("add")
@click.argument("project")
@click.argument("key")
def pin_add(project: str, key: str):
    """Pin KEY for PROJECT so it is skipped during rotation."""
    pins = pin_key(project, key)
    click.echo(f"Pinned '{key}' for project '{project}'.")
    click.echo(f"Pinned keys: {', '.join(pins)}")


@pin_cmd.command("remove")
@click.argument("project")
@click.argument("key")
def pin_remove(project: str, key: str):
    """Unpin KEY for PROJECT."""
    removed = unpin_key(project, key)
    if removed:
        click.echo(f"Unpinned '{key}' for project '{project}'.")
    else:
        click.echo(f"Key '{key}' was not pinned for project '{project}'.")
        raise SystemExit(1)


@pin_cmd.command("list")
@click.argument("project")
def pin_list(project: str):
    """List all pinned keys for PROJECT."""
    pins = get_pins(project)
    if not pins:
        click.echo(f"No pinned keys for project '{project}'.")
    else:
        click.echo(f"Pinned keys for '{project}':")
        for key in pins:
            click.echo(f"  - {key}")


@pin_cmd.command("check")
@click.argument("project")
@click.argument("key")
def pin_check(project: str, key: str):
    """Check whether KEY is pinned for PROJECT."""
    if is_pinned(project, key):
        click.echo(f"'{key}' is pinned for project '{project}'.")
    else:
        click.echo(f"'{key}' is NOT pinned for project '{project}'.")
        raise SystemExit(1)


@pin_cmd.command("clear")
@click.argument("project")
def pin_clear(project: str):
    """Clear all pinned keys for PROJECT."""
    count = clear_pins(project)
    click.echo(f"Cleared {count} pinned key(s) for project '{project}'.")
