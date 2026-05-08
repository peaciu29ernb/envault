"""CLI commands for exporting decrypted vault contents."""

import sys
import click
from envault.vault import load_vault
from envault.keystore import retrieve_key
from envault.export import export_env, SUPPORTED_FORMATS
from envault.audit import record_event


@click.group()
def export_cmd():
    """Export decrypted .env contents to various formats."""
    pass


@export_cmd.command("run")
@click.argument("vault_file")
@click.option(
    "--format", "-f",
    "fmt",
    default="env",
    show_default=True,
    type=click.Choice(SUPPORTED_FORMATS, case_sensitive=False),
    help="Output format.",
)
@click.option(
    "--project", "-p",
    default=None,
    help="Project name for keystore lookup (defaults to vault filename stem).",
)
@click.option(
    "--password",
    default=None,
    help="Password if vault was encrypted with a password.",
)
@click.option(
    "--output", "-o",
    default=None,
    type=click.Path(),
    help="Write output to file instead of stdout.",
)
def export_run(vault_file: str, fmt: str, project: str, password: str, output: str):
    """Decrypt VAULT_FILE and export its contents in the chosen format."""
    from pathlib import Path

    project = project or Path(vault_file).stem

    try:
        if password:
            env_dict = load_vault(vault_file, password=password)
        else:
            key = retrieve_key(project)
            env_dict = load_vault(vault_file, key=key)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except Exception as exc:
        click.echo(f"Error decrypting vault: {exc}", err=True)
        sys.exit(1)

    result = export_env(env_dict, fmt=fmt)

    record_event("export", project, details={"format": fmt, "vault": vault_file})

    if output:
        Path(output).write_text(result)
        click.echo(f"Exported {len(env_dict)} variable(s) to '{output}' [{fmt}].")
    else:
        click.echo(result, nl=False)
