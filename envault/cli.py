"""Main CLI entry point for envault."""

import click

from envault.vault import create_vault, load_vault, save_vault
from envault.keystore import store_key, retrieve_key
from envault.rotation import rotate_key
from envault.audit import record_event
from envault.cli_audit import audit_cmd
from envault.cli_export import export_cmd
from envault.cli_diff import diff_cmd
from envault.cli_snapshot import snapshot_cmd
from envault.cli_validate import validate_cmd
from envault.cli_profile import profile_cmd
from envault.cli_search import search_cmd
from envault.cli_history import history_cmd
from envault.cli_signing import signing_cmd
from envault.cli_pin import pin_cmd
from envault.cli_lock import lock_cmd
from envault.cli_namespace import namespace_cmd
from envault.cli_access import access_cmd
from envault.cli_scope import scope_cmd
from envault.cli_transform import transform_cmd
from envault.cli_inherit import inherit_cmd
from envault.cli_deprecate import deprecate_cmd
from envault.cli_classify import classify_cmd
from envault.cli_notify import notify_cmd
from envault.cli_pipeline import pipeline_cmd


@click.group()
def cli():
    """envault — encrypted .env manager with key rotation."""


@cli.command("init")
@click.argument("env_file")
@click.argument("vault_file")
@click.option("--project", default="default", show_default=True)
@click.option("--password", default=None, help="Derive key from password instead of random")
def init_vault(env_file: str, vault_file: str, project: str, password):
    """Encrypt ENV_FILE into VAULT_FILE and store the key."""
    try:
        with open(env_file) as fh:
            raw = fh.read()
    except FileNotFoundError:
        raise click.ClickException(f"File not found: {env_file}")

    kwargs = {"password": password} if password else {}
    key, path = create_vault(raw, vault_file, **kwargs)
    store_key(project, key)
    record_event(project, "init", {"vault": vault_file})
    click.echo(f"Vault created: {path}")
    click.echo(f"Key stored for project '{project}'")


@cli.command("decrypt")
@click.argument("vault_file")
@click.option("--project", default="default", show_default=True)
@click.option("--password", default=None)
def decrypt_vault(vault_file: str, project: str, password):
    """Decrypt VAULT_FILE and print env vars."""
    key = retrieve_key(project)
    kwargs = {"password": password} if password else {}
    env = load_vault(vault_file, key=key, **kwargs)
    record_event(project, "decrypt", {"vault": vault_file})
    for k, v in env.items():
        click.echo(f"{k}={v}")


@cli.command("rotate")
@click.argument("vault_file")
@click.option("--project", default="default", show_default=True)
def rotate(vault_file: str, project: str):
    """Rotate the encryption key for VAULT_FILE."""
    old_key = retrieve_key(project)
    new_key = rotate_key(vault_file, old_key)
    store_key(project, new_key)
    record_event(project, "rotate", {"vault": vault_file})
    click.echo(f"Key rotated for project '{project}'")


@cli.command("list")
def list_cmd():
    """List stored project names."""
    from envault.keystore import list_projects
    projects = list_projects()
    if not projects:
        click.echo("No projects found.")
    for name in projects:
        click.echo(name)


cli.add_command(audit_cmd, "audit")
cli.add_command(export_cmd, "export")
cli.add_command(diff_cmd, "diff")
cli.add_command(snapshot_cmd, "snapshot")
cli.add_command(validate_cmd, "validate")
cli.add_command(profile_cmd, "profile")
cli.add_command(search_cmd, "search")
cli.add_command(history_cmd, "history")
cli.add_command(signing_cmd, "sign")
cli.add_command(pin_cmd, "pin")
cli.add_command(lock_cmd, "lock")
cli.add_command(namespace_cmd, "namespace")
cli.add_command(access_cmd, "access")
cli.add_command(scope_cmd, "scope")
cli.add_command(transform_cmd, "transform")
cli.add_command(inherit_cmd, "inherit")
cli.add_command(deprecate_cmd, "deprecate")
cli.add_command(classify_cmd, "classify")
cli.add_command(notify_cmd, "notify")
cli.add_command(pipeline_cmd, "pipeline")
