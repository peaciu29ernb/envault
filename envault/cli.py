"""Command-line interface for envault."""

import sys
import click
from pathlib import Path

from envault.vault import create_vault, save_vault, load_vault
from envault.keystore import store_key, retrieve_key, delete_key, list_projects
from envault.rotation import rotate_key, rotate_password


@click.group()
def cli():
    """envault — encrypt and manage per-project .env files."""
    pass


@cli.command("init")
@click.argument("project")
@click.option("--env-file", default=".env", show_default=True, help="Path to .env file.")
@click.option("--password", default=None, help="Use password-based encryption.")
def init_vault(project, env_file, password):
    """Initialize a vault for PROJECT from an .env file."""
    env_path = Path(env_file)
    if not env_path.exists():
        click.echo(f"Error: {env_file} not found.", err=True)
        sys.exit(1)

    raw = env_path.read_text()
    vault, key = create_vault(raw, password=password)
    vault_path = Path(f"{project}.vault")
    save_vault(vault, vault_path)

    if key and not password:
        store_key(project, key)
        click.echo(f"Vault created at {vault_path}. Key stored in keystore.")
    else:
        click.echo(f"Vault created at {vault_path}. Use your password to decrypt.")


@cli.command("decrypt")
@click.argument("project")
@click.option("--vault-file", default=None, help="Path to vault file (default: <project>.vault).")
@click.option("--password", default=None, help="Password for decryption.")
@click.option("--output", default=".env", show_default=True, help="Output .env file path.")
def decrypt_vault(project, vault_file, password, output):
    """Decrypt a vault and write the .env file."""
    vault_path = Path(vault_file) if vault_file else Path(f"{project}.vault")
    if not vault_path.exists():
        click.echo(f"Error: {vault_path} not found.", err=True)
        sys.exit(1)

    key = None
    if not password:
        key = retrieve_key(project)

    env_dict = load_vault(vault_path, key=key, password=password)
    lines = "\n".join(f"{k}={v}" for k, v in env_dict.items())
    Path(output).write_text(lines + "\n")
    click.echo(f"Decrypted to {output}.")


@cli.command("rotate")
@click.argument("project")
@click.option("--vault-file", default=None, help="Path to vault file.")
def rotate(project, vault_file):
    """Rotate the encryption key for PROJECT."""
    vault_path = Path(vault_file) if vault_file else Path(f"{project}.vault")
    if not vault_path.exists():
        click.echo(f"Error: {vault_path} not found.", err=True)
        sys.exit(1)

    old_key = retrieve_key(project)
    new_vault, new_key = rotate_key(vault_path, old_key)
    save_vault(new_vault, vault_path)
    store_key(project, new_key)
    click.echo(f"Key rotated for project '{project}'.")


@cli.command("list")
def list_cmd():
    """List all projects in the keystore."""
    projects = list_projects()
    if not projects:
        click.echo("No projects found.")
    else:
        for p in projects:
            click.echo(p)


@cli.command("delete")
@click.argument("project")
def delete_cmd(project):
    """Remove a project key from the keystore."""
    removed = delete_key(project)
    if removed:
        click.echo(f"Key for '{project}' removed.")
    else:
        click.echo(f"No key found for '{project}'.")


if __name__ == "__main__":
    cli()
