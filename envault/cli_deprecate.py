"""CLI commands for managing deprecated env keys."""

from __future__ import annotations

import click

from envault.deprecate import (
    mark_deprecated,
    unmark_deprecated,
    list_deprecated,
    get_deprecation_info,
)


@click.group(name="deprecate")
def deprecate_cmd():
    """Manage deprecated env keys."""


@deprecate_cmd.command("add")
@click.argument("key")
@click.option("--reason", default="", help="Why this key is deprecated.")
@click.option("--replacement", default=None, help="Suggested replacement key.")
@click.option("--base-dir", default=".envault", show_default=True)
def deprecate_add(key: str, reason: str, replacement, base_dir: str):
    """Mark KEY as deprecated."""
    info = mark_deprecated(key, base_dir=base_dir, reason=reason, replacement=replacement)
    click.echo(f"Marked '{key}' as deprecated.")
    if reason:
        click.echo(f"  Reason: {reason}")
    if replacement:
        click.echo(f"  Replacement: {replacement}")


@deprecate_cmd.command("remove")
@click.argument("key")
@click.option("--base-dir", default=".envault", show_default=True)
def deprecate_remove(key: str, base_dir: str):
    """Remove deprecation marking from KEY."""
    removed = unmark_deprecated(key, base_dir=base_dir)
    if removed:
        click.echo(f"Removed deprecation for '{key}'.")
    else:
        click.echo(f"Key '{key}' was not marked as deprecated.", err=True)


@deprecate_cmd.command("list")
@click.option("--base-dir", default=".envault", show_default=True)
def deprecate_list(base_dir: str):
    """List all deprecated keys."""
    data = list_deprecated(base_dir=base_dir)
    if not data:
        click.echo("No deprecated keys.")
        return
    for key, info in data.items():
        repl = f" -> {info['replacement']}" if info.get("replacement") else ""
        reason = f" ({info['reason']})" if info.get("reason") else ""
        click.echo(f"  {key}{repl}{reason}")


@deprecate_cmd.command("check")
@click.argument("key")
@click.option("--base-dir", default=".envault", show_default=True)
def deprecate_check(key: str, base_dir: str):
    """Check if KEY is deprecated."""
    info = get_deprecation_info(key, base_dir=base_dir)
    if info is None:
        click.echo(f"'{key}' is not deprecated.")
    else:
        repl = f" Replacement: {info['replacement']}." if info.get("replacement") else ""
        reason = f" Reason: {info['reason']}." if info.get("reason") else ""
        click.echo(f"'{key}' is deprecated.{reason}{repl}")
