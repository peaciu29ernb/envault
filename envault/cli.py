"""Main CLI entry point for envault."""
from __future__ import annotations

import click

from envault.vault import create_vault, load_vault, save_vault
from envault.keystore import store_key, retrieve_key
from envault.rotation import rotate_key, rotate_password
from envault.cli_audit import audit_cmd
from envault.cli_export import export_cmd
from envault.cli_diff import diff_cmd
from envault.cli_snapshot import snapshot_cmd
from envault.cli_validate import validate_cmd
from envault.cli_profile import profile_cmd
from envault.cli_search import search_cmd
from envault.cli_history import history_cmd
from envault.cli_pin import pin_cmd
from envault.cli_scope import scope_cmd


@click.group()
def cli() -> None:
    """envault — encrypted .env manager."""


@cli.command("init")
@click.argument("project")
@click.argument("env_file", default=".env")
@click.option("--password", default=None, help="Encrypt with a password instead of a random key.")
def init_vault(project: str, env_file: str, password: str | None) -> None:
    """Encrypt ENV_FILE and store the vault for PROJECT."""
    try:
        vault, key = create_vault(env_file, password=password)
    except FileNotFoundError:
        raise click.ClickException(f"Env file not found: {env_file}")
    save_vault(vault, project)
    if key:
        store_key(project, key)
        click.echo(f"Vault created for '{project}'. Key stored in keystore.")
    else:
        click.echo(f"Vault created for '{project}' (password-protected).")


@cli.command("decrypt")
@click.argument("project")
@click.option("--password", default=None, help="Password (if vault is password-protected).")
def decrypt_vault(project: str, password: str | None) -> None:
    """Decrypt and print the env vars for PROJECT."""
    vault = load_vault(project)
    if password:
        from envault.crypto import decrypt_with_password
        data = decrypt_with_password(vault["ciphertext"], password)
    else:
        key = retrieve_key(project)
        from envault.crypto import decrypt
        data = decrypt(vault["ciphertext"], key)
    click.echo(data.decode())


@cli.command("rotate")
@click.argument("project")
@click.option("--password", default=None)
@click.option("--new-password", default=None)
def rotate(project: str, password: str | None, new_password: str | None) -> None:
    """Rotate encryption key/password for PROJECT."""
    if password or new_password:
        rotate_password(project, password, new_password)
        click.echo("Password rotated.")
    else:
        rotate_key(project)
        click.echo("Key rotated and stored.")


@cli.command("list")
def list_cmd() -> None:
    """List projects in the keystore."""
    from envault.keystore import list_projects
    projects = list_projects()
    if not projects:
        click.echo("No projects found.")
    else:
        for p in projects:
            click.echo(p)


cli.add_command(audit_cmd)
cli.add_command(export_cmd)
cli.add_command(diff_cmd)
cli.add_command(snapshot_cmd)
cli.add_command(validate_cmd)
cli.add_command(profile_cmd)
cli.add_command(search_cmd)
cli.add_command(history_cmd)
cli.add_command(pin_cmd)
cli.add_command(scope_cmd)
