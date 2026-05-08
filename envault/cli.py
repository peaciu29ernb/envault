"""Main CLI entry-point for envault."""

from __future__ import annotations

import click

from envault.audit import record_event
from envault.cli_audit import audit_cmd
from envault.cli_diff import diff_cmd
from envault.cli_export import export_cmd
from envault.cli_profile import profile_cmd
from envault.cli_snapshot import snapshot_cmd
from envault.cli_validate import validate_cmd
from envault.keystore import delete_key, list_projects, retrieve_key, store_key
from envault.rotation import rotate_key, rotate_password
from envault.vault import create_vault, load_vault, save_vault


@click.group()
def cli():
    """envault — encrypted .env manager."""


@cli.command("init")
@click.argument("project")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--password", default=None, help="Use password-based encryption")
def init_vault(project, env_file, password):
    """Encrypt an .env file and store the key."""
    with open(env_file) as fh:
        raw = fh.read()
    vault_file = f"{project}.vault"
    key, token = create_vault(raw, password=password)
    save_vault(token, vault_file)
    if key:
        store_key(project, key)
        click.echo(f"Vault created: {vault_file} (key stored for '{project}')")
    else:
        click.echo(f"Vault created: {vault_file} (password-protected)")
    record_event(project, "init", {"vault_file": vault_file, "password_based": key is None})


@cli.command("decrypt")
@click.argument("project")
@click.argument("vault_file", type=click.Path(exists=True))
@click.option("--password", default=None)
def decrypt_vault(project, vault_file, password):
    """Decrypt a vault file and print its contents."""
    key = None
    if not password:
        key = retrieve_key(project)
    env = load_vault(vault_file, key=key, password=password)
    for k, v in env.items():
        click.echo(f"{k}={v}")
    record_event(project, "decrypt", {"vault_file": vault_file})


@cli.command("rotate")
@click.argument("project")
@click.argument("vault_file", type=click.Path(exists=True))
@click.option("--new-password", default=None)
def rotate(project, vault_file, new_password):
    """Rotate the encryption key for a vault."""
    old_key = retrieve_key(project)
    if new_password:
        new_token = rotate_password(vault_file, old_key=old_key, new_password=new_password)
        save_vault(new_token, vault_file)
        click.echo("Vault re-encrypted with new password.")
    else:
        new_key, new_token = rotate_key(vault_file, old_key=old_key)
        save_vault(new_token, vault_file)
        store_key(project, new_key)
        click.echo(f"Key rotated for '{project}'.")
    record_event(project, "rotate", {"vault_file": vault_file})


@cli.command("list")
def list_cmd():
    """List all projects with stored keys."""
    projects = list_projects()
    if not projects:
        click.echo("No projects found.")
    for p in projects:
        click.echo(p)


@cli.command("delete")
@click.argument("project")
def delete_cmd(project):
    """Remove a stored key for a project."""
    removed = delete_key(project)
    if removed:
        click.echo(f"Key for '{project}' deleted.")
        record_event(project, "delete_key", {})
    else:
        click.echo(f"No key found for '{project}'.")


cli.add_command(audit_cmd)
cli.add_command(export_cmd)
cli.add_command(diff_cmd)
cli.add_command(snapshot_cmd)
cli.add_command(validate_cmd)
cli.add_command(profile_cmd)

if __name__ == "__main__":
    cli()
