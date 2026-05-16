"""CLI commands for promoting env vars between profiles."""

from __future__ import annotations

import json

import click

from envault.promote import PromoteError, promote_keys, promote_report
from envault.vault import load_vault, save_vault


@click.group(name="promote")
def promote_cmd() -> None:
    """Promote environment variables from one vault to another."""


@promote_cmd.command(name="run")
@click.argument("source_vault")
@click.argument("target_vault")
@click.option("--keys", "-k", multiple=True, help="Keys to promote (default: all).")
@click.option("--exclude", "-e", multiple=True, help="Keys to skip.")
@click.option("--overwrite", is_flag=True, default=False,
              help="Overwrite existing keys in target.")
@click.option("--dry-run", is_flag=True, default=False,
              help="Show what would change without writing.")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]),
              default="text", show_default=True)
def promote_run(
    source_vault: str,
    target_vault: str,
    keys: tuple,
    exclude: tuple,
    overwrite: bool,
    dry_run: bool,
    fmt: str,
) -> None:
    """Promote keys from SOURCE_VAULT into TARGET_VAULT."""
    src_env, src_key = load_vault(source_vault)
    tgt_env, tgt_key = load_vault(target_vault)

    try:
        result = promote_keys(
            source=src_env,
            target=tgt_env,
            keys=list(keys) if keys else None,
            overwrite=overwrite,
            exclude=list(exclude),
        )
    except PromoteError as exc:
        raise click.ClickException(str(exc)) from exc

    report = promote_report(src_env, tgt_env, result)

    if fmt == "json":
        click.echo(json.dumps(report, indent=2))
    else:
        for entry in report:
            action = entry["action"]
            key = entry["key"]
            if action == "added":
                click.echo(f"  + {key} (added)")
            elif action == "overwritten":
                click.echo(f"  ~ {key}: {entry['old']!r} -> {entry['value']!r}")
            else:
                click.echo(f"    {key} (unchanged)")

    if dry_run:
        click.echo("\n[dry-run] No changes written.")
        return

    save_vault(target_vault, result, tgt_key)
    click.echo(f"\nPromoted to {target_vault}.")
