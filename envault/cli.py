"""Main CLI entry-point for envault."""

from __future__ import annotations

import click

from envault.vault import create_vault, save_vault, load_vault
from envault.keystore import store_key, retrieve_key, list_projects
from envault.cli_audit import audit_cmd
from envault.cli_export import export_cmd
from envault.cli_diff import diff_cmd
from envault.cli_snapshot import snapshot_cmd
from envault.cli_validate import validate_cmd
from envault.cli_profile import profile_cmd
from envault.cli_search import search_cmd


@click.group()
def cli() -> None:
    """envault — encrypted .env manager."""


@cli.command("init")
@click.option("--env", "env_path", default=".env", show_default=True)
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--project", default="default", show_default=True)
@click.option("--password", default=None, help="Derive key from password instead.")
def init_vault(env_path: str, vault_path: str, project: str, password: str | None) -> None:
    """Encrypt an existing .env file into a vault."""
    try:
        with open(env_path) as fh:
            env_text = fh.read()
    except FileNotFoundError:
        raise click.ClickException(f"File not found: {env_path}")

    vault, key = create_vault(env_text, password=password)
    save_vault(vault, vault_path)

    if key:
        store_key(project, key)
        click.echo(f"Key stored for project '{project}'.")
    click.echo(f"Vault written to {vault_path}")


@cli.command("decrypt")
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--project", default="default", show_default=True)
@click.option("--password", default=None)
def decrypt_vault(vault_path: str, project: str, password: str | None) -> None:
    """Decrypt and print vault contents."""
    key: bytes | None = None
    if not password:
        key = retrieve_key(project)
    env = load_vault(vault_path, key=key, password=password)
    for k, v in env.items():
        click.echo(f"{k}={v}")


@cli.command("rotate")
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--project", default="default", show_default=True)
def rotate(vault_path: str, project: str) -> None:
    """Rotate the encryption key for a vault."""
    from envault.rotation import rotate_key

    old_key = retrieve_key(project)
    new_vault, new_key = rotate_key(vault_path, old_key)
    save_vault(new_vault, vault_path)
    store_key(project, new_key)
    click.echo("Key rotated successfully.")


@cli.command("list")
def list_cmd() -> None:
    """List all known projects."""
    projects = list_projects()
    if not projects:
        click.echo("No projects found.")
        return
    for p in projects:
        click.echo(p)


# Register sub-command groups
cli.add_command(audit_cmd)
cli.add_command(export_cmd)
cli.add_command(diff_cmd)
cli.add_command(snapshot_cmd)
cli.add_command(validate_cmd)
cli.add_command(profile_cmd)
cli.add_command(search_cmd)

if __name__ == "__main__":
    cli()
