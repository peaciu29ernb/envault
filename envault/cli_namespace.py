"""CLI commands for namespace management."""

import os
import click
from envault.namespace import (
    add_to_namespace,
    remove_from_namespace,
    get_namespace_keys,
    list_namespaces,
    resolve_namespace,
)

_DEFAULT_BASE = os.path.expanduser("~/.envault")


@click.group(name="namespace")
def namespace_cmd():
    """Manage key namespaces for a project."""


@namespace_cmd.command("add")
@click.argument("project")
@click.argument("namespace")
@click.argument("key")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def namespace_add(project, namespace, key, base_dir):
    """Add KEY to NAMESPACE in PROJECT."""
    keys = add_to_namespace(project, namespace, key, base_dir)
    click.echo(f"Added '{key}' to namespace '{namespace}'.")
    click.echo("Keys: " + ", ".join(keys))


@namespace_cmd.command("remove")
@click.argument("project")
@click.argument("namespace")
@click.argument("key")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def namespace_remove(project, namespace, key, base_dir):
    """Remove KEY from NAMESPACE in PROJECT."""
    removed = remove_from_namespace(project, namespace, key, base_dir)
    if removed:
        click.echo(f"Removed '{key}' from namespace '{namespace}'.")
    else:
        click.echo(f"Key '{key}' not found in namespace '{namespace}'.")


@namespace_cmd.command("list")
@click.argument("project")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def namespace_list(project, base_dir):
    """List all namespaces for PROJECT."""
    namespaces = list_namespaces(project, base_dir)
    if not namespaces:
        click.echo("No namespaces defined.")
    else:
        for ns in namespaces:
            click.echo(ns)


@namespace_cmd.command("show")
@click.argument("project")
@click.argument("namespace")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def namespace_show(project, namespace, base_dir):
    """Show keys in NAMESPACE for PROJECT."""
    keys = get_namespace_keys(project, namespace, base_dir)
    if not keys:
        click.echo(f"Namespace '{namespace}' is empty or does not exist.")
    else:
        for key in keys:
            click.echo(key)


@namespace_cmd.command("resolve")
@click.argument("project")
@click.argument("key")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def namespace_resolve(project, key, base_dir):
    """Find which namespace contains KEY in PROJECT."""
    ns = resolve_namespace(project, key, base_dir)
    if ns:
        click.echo(f"'{key}' belongs to namespace '{ns}'.")
    else:
        click.echo(f"'{key}' is not assigned to any namespace.")
