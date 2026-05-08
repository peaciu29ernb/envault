"""Main CLI entry point for envault."""

import sys
import click
from envault.vault import create_vault, save_vault, load_vault
from envault.keystore import store_key, retrieve_key, list_projects
from envault.rotation import rotate_key, rotate_password
from envault.audit import record_event
from envault.cli_audit import audit_cmd
from envault.cli_export import export_cmd


@click.group()
def cli():
    """envault — encrypt and manage per-project .env files."""
    pass


@cli.command()
@click.argument("env_file")
@click.argument("vault_file")
@click.option("--project", "-p", default=None, help="Project name (defaults to vault filename stem).")
@click.option("--password", default=None, help="Encrypt with a password instead of a generated key.")
def init_vault(env_file: str, vault_file: str, project: str, password: str):
    """Encrypt ENV_FILE into VAULT_FILE."""
    from pathlib import Path
    project = project or Path(vault_file).stem
    try:
        env_text = Path(env_file).read_text()
    except FileNotFoundError:
        click.echo(f"Error: env file '{env_file}' not found.", err=True)
        sys.exit(1)

    if password:
        vault_data, _ = create_vault(env_text, password=password)
        click.echo("Vault created with password encryption.")
    else:
        vault_data, key = create_vault(env_text)
        store_key(project, key)
        click.echo(f"Vault created. Key stored for project '{project}'.")

    save_vault(vault_data, vault_file)
    record_event("init", project, details={"vault": vault_file})
    click.echo(f"Vault saved to '{vault_file}'.")


@cli.command("decrypt")
@click.argument("vault_file")
@click.option("--project", "-p", default=None)
@click.option("--password", default=None)
def decrypt_vault(vault_file: str, project: str, password: str):
    """Decrypt VAULT_FILE and print its contents."""
    from pathlib import Path
    project = project or Path(vault_file).stem
    try:
        if password:
            env_dict = load_vault(vault_file, password=password)
        else:
            key = retrieve_key(project)
            env_dict = load_vault(vault_file, key=key)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    record_event("decrypt", project, details={"vault": vault_file})
    for k, v in env_dict.items():
        click.echo(f"{k}={v}")


@cli.command()
@click.argument("vault_file")
@click.option("--project", "-p", default=None)
def rotate(vault_file: str, project: str):
    """Rotate the encryption key for VAULT_FILE."""
    from pathlib import Path
    project = project or Path(vault_file).stem
    try:
        old_key = retrieve_key(project)
        new_vault, new_key = rotate_key(vault_file, old_key)
        save_vault(new_vault, vault_file)
        store_key(project, new_key)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    record_event("rotate", project, details={"vault": vault_file})
    click.echo(f"Key rotated for project '{project}'.")


@cli.command("list")
def list_cmd():
    """List all projects with stored keys."""
    projects = list_projects()
    if not projects:
        click.echo("No projects found.")
    else:
        for p in projects:
            click.echo(p)


@cli.command("export")
@click.pass_context
def export_alias(ctx):
    """Alias — use 'envault export run' instead."""
    click.echo("Use: envault export run <vault_file> [options]")


cli.add_command(audit_cmd, name="audit")
cli.add_command(export_cmd, name="export")


if __name__ == "__main__":
    cli()
