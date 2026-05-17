"""CLI commands for pruning keys from an encrypted vault."""

from __future__ import annotations

import json
import sys

import click

from envault.prune import (
    PruneError,
    prune_by_glob,
    prune_by_keys,
    prune_by_regex,
    prune_empty,
    prune_report,
)
from envault.vault import load_vault, save_vault


@click.group(name="prune")
def prune_cmd() -> None:
    """Remove unwanted keys from a vault."""


def _common_options(fn):
    fn = click.option("--vault", default=".env.vault", show_default=True, help="Vault file path.")(fn)
    fn = click.option("--key", "enc_key", envvar="ENVAULT_KEY", required=True, help="Encryption key.")(fn)
    fn = click.option("--dry-run", is_flag=True, help="Preview changes without writing.")(fn)
    fn = click.option("--json", "as_json", is_flag=True, help="Output report as JSON.")(fn)
    return fn


def _finish(env_before, new_env, removed, vault_path, enc_key, dry_run, as_json):
    report = prune_report(removed, total_before=len(env_before))
    if as_json:
        click.echo(json.dumps(report, indent=2))
    else:
        if removed:
            click.echo(f"Removed {len(removed)} key(s): {', '.join(removed)}")
        else:
            click.echo("No keys matched — nothing removed.")
    if not dry_run and removed:
        save_vault(vault_path, new_env, enc_key)
        if not as_json:
            click.echo(f"Vault updated: {vault_path}")


@prune_cmd.command(name="keys")
@click.argument("key_names", nargs=-1, required=True)
@click.option("--missing-ok", is_flag=True, default=True)
@_common_options
def prune_keys(key_names, vault, enc_key, dry_run, as_json, missing_ok):
    """Remove specific KEY_NAMES from the vault."""
    env = load_vault(vault, enc_key)
    try:
        new_env, removed = prune_by_keys(env, list(key_names), missing_ok=missing_ok)
    except PruneError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    _finish(env, new_env, removed, vault, enc_key, dry_run, as_json)


@prune_cmd.command(name="glob")
@click.argument("pattern")
@_common_options
def prune_glob(pattern, vault, enc_key, dry_run, as_json):
    """Remove keys whose names match a glob PATTERN (e.g. 'TMP_*')."""
    env = load_vault(vault, enc_key)
    new_env, removed = prune_by_glob(env, pattern)
    _finish(env, new_env, removed, vault, enc_key, dry_run, as_json)


@prune_cmd.command(name="regex")
@click.argument("pattern")
@_common_options
def prune_regex(pattern, vault, enc_key, dry_run, as_json):
    """Remove keys whose names match a regular expression PATTERN."""
    env = load_vault(vault, enc_key)
    try:
        new_env, removed = prune_by_regex(env, pattern)
    except PruneError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    _finish(env, new_env, removed, vault, enc_key, dry_run, as_json)


@prune_cmd.command(name="empty")
@_common_options
def prune_empty_cmd(vault, enc_key, dry_run, as_json):
    """Remove keys with empty or whitespace-only values."""
    env = load_vault(vault, enc_key)
    new_env, removed = prune_empty(env)
    _finish(env, new_env, removed, vault, enc_key, dry_run, as_json)
