"""CLI commands for vault snapshots."""

import click
from click import echo

from envault.snapshot import (
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)
from envault.vault import load_vault
from envault.diff import diff_envs, format_diff


@click.group("snapshot")
def snapshot_cmd():
    """Manage named snapshots of vault contents."""


@snapshot_cmd.command("save")
@click.argument("project")
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--name", default=None, help="Snapshot name (default: timestamp)")
@click.option("--key", "key_hex", default=None, envvar="ENVAULT_KEY")
@click.option("--password", default=None, envvar="ENVAULT_PASSWORD")
def snapshot_save(project, vault_path, name, key_hex, password):
    """Save a snapshot of the current vault state."""
    try:
        key = bytes.fromhex(key_hex) if key_hex else None
        env = load_vault(vault_path, key=key, password=password)
        record = save_snapshot(project, env, name=name)
        echo(f"Snapshot '{record['name']}' saved for project '{project}'.")
    except Exception as exc:
        echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@snapshot_cmd.command("list")
@click.argument("project")
def snapshot_list(project):
    """List saved snapshots for a project."""
    names = list_snapshots(project)
    if not names:
        echo(f"No snapshots found for project '{project}'.")
    else:
        for n in names:
            echo(n)


@snapshot_cmd.command("diff")
@click.argument("project")
@click.argument("snapshot_name")
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--key", "key_hex", default=None, envvar="ENVAULT_KEY")
@click.option("--password", default=None, envvar="ENVAULT_PASSWORD")
def snapshot_diff(project, snapshot_name, vault_path, key_hex, password):
    """Diff current vault against a saved snapshot."""
    try:
        key = bytes.fromhex(key_hex) if key_hex else None
        current = load_vault(vault_path, key=key, password=password)
        record = load_snapshot(project, snapshot_name)
        changes = diff_envs(record["env"], current)
        echo(format_diff(changes))
    except Exception as exc:
        echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@snapshot_cmd.command("delete")
@click.argument("project")
@click.argument("snapshot_name")
def snapshot_delete(project, snapshot_name):
    """Delete a named snapshot."""
    removed = delete_snapshot(project, snapshot_name)
    if removed:
        echo(f"Snapshot '{snapshot_name}' deleted.")
    else:
        echo(f"Snapshot '{snapshot_name}' not found.", err=True)
        raise SystemExit(1)
