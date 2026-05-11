"""CLI commands for scope management."""
from __future__ import annotations

import click

from envault import scope as sc

_DEFAULT_BASE = click.get_app_dir("envault") + "/scopes"


@click.group(name="scope")
def scope_cmd() -> None:
    """Manage key scopes (dev, prod, ci, …)."""


@scope_cmd.command("add")
@click.argument("project")
@click.argument("scope")
@click.argument("key")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def scope_add(project: str, scope: str, key: str, base_dir: str) -> None:
    """Add KEY to SCOPE for PROJECT."""
    keys = sc.add_to_scope(base_dir, project, scope, key)
    click.echo(f"Added '{key}' to scope '{scope}'. Keys: {', '.join(keys)}")


@scope_cmd.command("remove")
@click.argument("project")
@click.argument("scope")
@click.argument("key")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def scope_remove(project: str, scope: str, key: str, base_dir: str) -> None:
    """Remove KEY from SCOPE for PROJECT."""
    removed = sc.remove_from_scope(base_dir, project, scope, key)
    if removed:
        click.echo(f"Removed '{key}' from scope '{scope}'.")
    else:
        click.echo(f"Key '{key}' not found in scope '{scope}'.")


@scope_cmd.command("list")
@click.argument("project")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def scope_list(project: str, base_dir: str) -> None:
    """List all scopes for PROJECT."""
    scopes = sc.list_scopes(base_dir, project)
    if not scopes:
        click.echo("No scopes defined.")
    else:
        for s in scopes:
            keys = sc.get_scope_keys(base_dir, project, s)
            click.echo(f"  {s}: {', '.join(keys) if keys else '(empty)'}")


@scope_cmd.command("show")
@click.argument("project")
@click.argument("scope")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def scope_show(project: str, scope: str, base_dir: str) -> None:
    """Show keys in SCOPE for PROJECT."""
    keys = sc.get_scope_keys(base_dir, project, scope)
    if not keys:
        click.echo(f"Scope '{scope}' is empty or does not exist.")
    else:
        for k in keys:
            click.echo(k)


@scope_cmd.command("which")
@click.argument("project")
@click.argument("key")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def scope_which(project: str, key: str, base_dir: str) -> None:
    """Show which scopes contain KEY for PROJECT."""
    scopes = sc.key_scopes(base_dir, project, key)
    if not scopes:
        click.echo(f"Key '{key}' is not in any scope.")
    else:
        click.echo(", ".join(scopes))
