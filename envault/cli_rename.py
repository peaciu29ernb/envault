"""CLI commands for key renaming in envault."""

import click
from envault.vault import load_vault, save_vault
from envault.keystore import retrieve_key
from envault.rename import rename_key, rename_bulk, rename_by_prefix, RenameError


@click.group(name="rename")
def rename_cmd():
    """Rename keys inside an encrypted vault."""


@rename_cmd.command("key")
@click.argument("vault_file")
@click.argument("old_key")
@click.argument("new_key")
@click.option("--project", default="default", show_default=True, help="Keystore project name.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite new_key if it already exists.")
def rename_single(vault_file, old_key, new_key, project, overwrite):
    """Rename OLD_KEY to NEW_KEY inside VAULT_FILE."""
    try:
        key = retrieve_key(project)
        env = load_vault(vault_file, key=key)
        updated = rename_key(env, old_key, new_key, overwrite=overwrite)
        save_vault(vault_file, updated, key=key)
        click.echo(f"Renamed '{old_key}' -> '{new_key}' in {vault_file}")
    except RenameError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@rename_cmd.command("prefix")
@click.argument("vault_file")
@click.argument("old_prefix")
@click.argument("new_prefix")
@click.option("--project", default="default", show_default=True, help="Keystore project name.")
@click.option("--overwrite", is_flag=True, default=False)
def rename_prefix(vault_file, old_prefix, new_prefix, project, overwrite):
    """Rename all keys sharing OLD_PREFIX to use NEW_PREFIX."""
    try:
        key = retrieve_key(project)
        env = load_vault(vault_file, key=key)
        updated = rename_by_prefix(env, old_prefix, new_prefix, overwrite=overwrite)
        changed = [
            k for k in env if k.startswith(old_prefix)
        ]
        save_vault(vault_file, updated, key=key)
        click.echo(f"Renamed {len(changed)} key(s) with prefix '{old_prefix}' -> '{new_prefix}'")
    except RenameError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
