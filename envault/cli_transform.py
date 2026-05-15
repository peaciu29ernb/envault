"""CLI commands for applying value transforms to vault env files."""

import json
import click
from envault.vault import load_vault, save_vault
from envault.transform import transform_env, list_transforms, TransformError


@click.group("transform")
def transform_cmd():
    """Apply value transformations to vault env variables."""


@transform_cmd.command("apply")
@click.argument("vault_file")
@click.argument("key")
@click.argument("transforms", nargs=-1, required=True)
@click.option("--password", default=None, help="Vault password (if password-protected).")
@click.option("--dry-run", is_flag=True, default=False, help="Print result without saving.")
def transform_apply(vault_file, key, transforms, password, dry_run):
    """Apply one or more TRANSFORMs to KEY in VAULT_FILE."""
    try:
        env = load_vault(vault_file, password=password)
    except Exception as exc:
        raise click.ClickException(f"Failed to load vault: {exc}")

    if key not in env:
        raise click.ClickException(f"Key '{key}' not found in vault.")

    rules = {key: list(transforms)}
    try:
        updated = transform_env(env, rules)
    except TransformError as exc:
        raise click.ClickException(str(exc))

    new_val = updated[key]
    if dry_run:
        click.echo(f"{key}={new_val}")
        return

    try:
        save_vault(vault_file, updated, password=password)
    except Exception as exc:
        raise click.ClickException(f"Failed to save vault: {exc}")

    click.echo(f"Transformed '{key}' → {new_val}")


@transform_cmd.command("batch")
@click.argument("vault_file")
@click.argument("rules_file")
@click.option("--password", default=None, help="Vault password.")
@click.option("--dry-run", is_flag=True, default=False)
def transform_batch(vault_file, rules_file, password, dry_run):
    """Apply transforms from a JSON RULES_FILE to VAULT_FILE.

    RULES_FILE format: {"KEY_OR_GLOB": ["transform1", "transform2"]}
    """
    try:
        with open(rules_file) as f:
            rules = json.load(f)
    except Exception as exc:
        raise click.ClickException(f"Failed to read rules file: {exc}")

    try:
        env = load_vault(vault_file, password=password)
    except Exception as exc:
        raise click.ClickException(f"Failed to load vault: {exc}")

    try:
        updated = transform_env(env, rules)
    except TransformError as exc:
        raise click.ClickException(str(exc))

    changed = {k for k in updated if updated[k] != env.get(k)}
    if dry_run:
        for k in sorted(changed):
            click.echo(f"{k}: {env[k]!r} → {updated[k]!r}")
        return

    try:
        save_vault(vault_file, updated, password=password)
    except Exception as exc:
        raise click.ClickException(f"Failed to save vault: {exc}")

    click.echo(f"Transformed {len(changed)} key(s): {', '.join(sorted(changed))}")


@transform_cmd.command("list")
def transform_list():
    """List all available built-in transforms."""
    for name in list_transforms():
        click.echo(name)
