"""CLI commands for reordering env keys."""

from __future__ import annotations

import click

from envault.reorder import (
    ReorderError,
    move_to_bottom,
    move_to_top,
    reorder_alphabetical,
    reorder_by_prefix,
)
from envault.vault import load_vault, save_vault


@click.group(name="reorder")
def reorder_cmd() -> None:
    """Reorder keys inside an encrypted vault."""


@reorder_cmd.command("alpha")
@click.argument("vault_path")
@click.argument("key")
@click.option("--reverse", is_flag=True, default=False, help="Sort Z→A.")
@click.option("--dry-run", is_flag=True, default=False)
def reorder_alpha(vault_path: str, key: str, reverse: bool, dry_run: bool) -> None:
    """Sort all keys alphabetically."""
    env = load_vault(vault_path, key)
    ordered = reorder_alphabetical(env, reverse=reverse)
    if dry_run:
        for k in ordered:
            click.echo(k)
        return
    save_vault(vault_path, ordered, key)
    click.echo(f"Reordered {len(ordered)} keys alphabetically.")


@reorder_cmd.command("by-prefix")
@click.argument("vault_path")
@click.argument("key")
@click.argument("prefixes", nargs=-1, required=True)
@click.option("--dry-run", is_flag=True, default=False)
def reorder_prefix(vault_path: str, key: str, prefixes: tuple, dry_run: bool) -> None:
    """Reorder keys by prefix groups."""
    env = load_vault(vault_path, key)
    ordered = reorder_by_prefix(env, list(prefixes))
    if dry_run:
        for k in ordered:
            click.echo(k)
        return
    save_vault(vault_path, ordered, key)
    click.echo(f"Reordered {len(ordered)} keys by prefix.")


@reorder_cmd.command("top")
@click.argument("vault_path")
@click.argument("key")
@click.argument("keys", nargs=-1, required=True)
@click.option("--dry-run", is_flag=True, default=False)
def reorder_top(vault_path: str, key: str, keys: tuple, dry_run: bool) -> None:
    """Move specified keys to the top."""
    env = load_vault(vault_path, key)
    ordered = move_to_top(env, list(keys))
    if dry_run:
        for k in ordered:
            click.echo(k)
        return
    save_vault(vault_path, ordered, key)
    click.echo(f"Moved {len(keys)} key(s) to top.")


@reorder_cmd.command("bottom")
@click.argument("vault_path")
@click.argument("key")
@click.argument("keys", nargs=-1, required=True)
@click.option("--dry-run", is_flag=True, default=False)
def reorder_bottom(vault_path: str, key: str, keys: tuple, dry_run: bool) -> None:
    """Move specified keys to the bottom."""
    env = load_vault(vault_path, key)
    ordered = move_to_bottom(env, list(keys))
    if dry_run:
        for k in ordered:
            click.echo(k)
        return
    save_vault(vault_path, ordered, key)
    click.echo(f"Moved {len(keys)} key(s) to bottom.")
