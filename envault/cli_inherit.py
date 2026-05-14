"""CLI commands for managing environment inheritance."""

from __future__ import annotations

import click

from envault.inherit import get_parents, remove_parent, set_parent


@click.group(name="inherit")
def inherit_cmd() -> None:
    """Manage environment inheritance between projects."""


@inherit_cmd.command("add")
@click.argument("project")
@click.argument("parent")
@click.option("--base-dir", default=".envault", show_default=True)
def inherit_add(project: str, parent: str, base_dir: str) -> None:
    """Register PARENT as an inheritance source for PROJECT."""
    set_parent(project, parent, base_dir=base_dir)
    click.echo(f"Project '{project}' now inherits from '{parent}'.")


@inherit_cmd.command("remove")
@click.argument("project")
@click.argument("parent")
@click.option("--base-dir", default=".envault", show_default=True)
def inherit_remove(project: str, parent: str, base_dir: str) -> None:
    """Remove PARENT from PROJECT's inheritance chain."""
    removed = remove_parent(project, parent, base_dir=base_dir)
    if removed:
        click.echo(f"Removed '{parent}' from '{project}' inheritance chain.")
    else:
        click.echo(f"'{parent}' was not a parent of '{project}'.")
        raise SystemExit(1)


@inherit_cmd.command("list")
@click.argument("project")
@click.option("--base-dir", default=".envault", show_default=True)
def inherit_list(project: str, base_dir: str) -> None:
    """List all parent projects for PROJECT."""
    parents = get_parents(project, base_dir=base_dir)
    if not parents:
        click.echo(f"No inheritance configured for '{project}'.")
        return
    click.echo(f"Inheritance chain for '{project}':")
    for idx, p in enumerate(parents, 1):
        click.echo(f"  {idx}. {p}")
