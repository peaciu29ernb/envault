"""cli_classify.py — CLI commands for classifying env keys."""

import click
from envault.classify import classify_env, keys_in_category, list_categories
from envault.vault import load_vault


@click.group(name="classify")
def classify_cmd():
    """Classify env keys into logical categories."""


@classify_cmd.command("show")
@click.argument("vault_file")
@click.option("--key", default=None, envvar="ENVAULT_KEY", help="Hex-encoded encryption key.")
@click.option("--password", default=None, help="Password for decryption.")
@click.option("--category", default=None, help="Filter output to a single category.")
def classify_show(vault_file: str, key: Optional[str], password: Optional[str], category: Optional[str]):
    """Show classified groups of keys from a vault."""
    import binascii

    raw_key = bytes.fromhex(key) if key else None
    try:
        env = load_vault(vault_file, key=raw_key, password=password)
    except Exception as exc:
        raise click.ClickException(str(exc))

    if category:
        keys = keys_in_category(env, category)
        if not keys:
            click.echo(f"No keys found in category '{category}'.")
        else:
            click.echo(f"[{category}]")
            for k in keys:
                click.echo(f"  {k}")
        return

    classified = classify_env(env)
    if not classified:
        click.echo("No keys found.")
        return

    for cat, keys in sorted(classified.items()):
        click.echo(f"[{cat}]")
        for k in keys:
            click.echo(f"  {k}")


@classify_cmd.command("list-categories")
def classify_list_categories():
    """List all built-in classification categories."""
    for cat in list_categories():
        click.echo(cat)


try:
    from typing import Optional
except ImportError:
    pass
