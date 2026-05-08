"""CLI commands for profile management."""

from __future__ import annotations

import json
from pathlib import Path

import click

from envault.profile import (
    delete_profile,
    diff_profiles,
    list_profiles,
    load_profile,
    save_profile,
)
from envault.vault import load_vault


@click.group("profile")
def profile_cmd():
    """Manage named env profiles (dev, staging, prod, …)."""


@profile_cmd.command("save")
@click.argument("project")
@click.argument("profile")
@click.argument("vault_file", type=click.Path(exists=True))
@click.option("--key", "key_hex", default=None, help="Hex-encoded decryption key")
@click.option("--password", default=None, help="Password for decryption")
def profile_save(project, profile, vault_file, key_hex, password):
    """Save current vault contents as a named profile."""
    key = bytes.fromhex(key_hex) if key_hex else None
    env = load_vault(vault_file, key=key, password=password)
    path = save_profile(project, profile, env)
    click.echo(f"Profile '{profile}' saved to {path}")


@profile_cmd.command("load")
@click.argument("project")
@click.argument("profile")
def profile_load(project, profile):
    """Print a profile's key=value pairs."""
    try:
        data = load_profile(project, profile)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    for k, v in data.items():
        click.echo(f"{k}={v}")


@profile_cmd.command("list")
@click.argument("project")
def profile_list(project):
    """List all profiles for a project."""
    profiles = list_profiles(project)
    if not profiles:
        click.echo("No profiles found.")
    for p in profiles:
        click.echo(p)


@profile_cmd.command("delete")
@click.argument("project")
@click.argument("profile")
def profile_delete(project, profile):
    """Delete a named profile."""
    removed = delete_profile(project, profile)
    if removed:
        click.echo(f"Profile '{profile}' deleted.")
    else:
        click.echo(f"Profile '{profile}' not found.")


@profile_cmd.command("diff")
@click.argument("project")
@click.argument("profile_a")
@click.argument("profile_b")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def profile_diff(project, profile_a, profile_b, as_json):
    """Show differences between two profiles."""
    try:
        changes = diff_profiles(project, profile_a, profile_b)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    if as_json:
        click.echo(json.dumps(changes, indent=2))
        return
    if not changes:
        click.echo("Profiles are identical.")
        return
    for key, info in changes.items():
        status = info["status"]
        if status == "added":
            click.echo(f"+ {key}={info['value']}")
        elif status == "removed":
            click.echo(f"- {key}={info['value']}")
        else:
            click.echo(f"~ {key}: {info['from']} -> {info['to']}")
