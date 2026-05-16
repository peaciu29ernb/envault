"""CLI commands for managing per-key annotations."""

from __future__ import annotations

import click

from envault.annotation import (
    set_annotation,
    get_annotation,
    remove_annotation,
    list_annotations,
)


@click.group(name="annotation")
def annotation_cmd() -> None:
    """Manage human-readable notes attached to env keys."""


@annotation_cmd.command("set")
@click.argument("key")
@click.argument("note")
@click.option("--project", default="default", show_default=True)
@click.option("--base-dir", default=".envault", show_default=True)
def annotation_set(key: str, note: str, project: str, base_dir: str) -> None:
    """Attach NOTE to KEY."""
    set_annotation(key, note, project=project, base_dir=base_dir)
    click.echo(f"Annotated '{key}': {note}")


@annotation_cmd.command("get")
@click.argument("key")
@click.option("--project", default="default", show_default=True)
@click.option("--base-dir", default=".envault", show_default=True)
def annotation_get(key: str, project: str, base_dir: str) -> None:
    """Show the annotation for KEY."""
    note = get_annotation(key, project=project, base_dir=base_dir)
    if note is None:
        click.echo(f"No annotation for '{key}'.")
    else:
        click.echo(f"{key}: {note}")


@annotation_cmd.command("remove")
@click.argument("key")
@click.option("--project", default="default", show_default=True)
@click.option("--base-dir", default=".envault", show_default=True)
def annotation_remove(key: str, project: str, base_dir: str) -> None:
    """Remove the annotation for KEY."""
    removed = remove_annotation(key, project=project, base_dir=base_dir)
    if removed:
        click.echo(f"Removed annotation for '{key}'.")
    else:
        click.echo(f"No annotation found for '{key}'.")


@annotation_cmd.command("list")
@click.option("--project", default="default", show_default=True)
@click.option("--base-dir", default=".envault", show_default=True)
def annotation_list(project: str, base_dir: str) -> None:
    """List all annotations for a project."""
    notes = list_annotations(project=project, base_dir=base_dir)
    if not notes:
        click.echo("No annotations found.")
        return
    for key, note in sorted(notes.items()):
        click.echo(f"  {key}: {note}")
