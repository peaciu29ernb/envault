"""CLI commands for searching/filtering vault contents."""

from __future__ import annotations

import click

from envault.vault import load_vault
from envault.search import search_keys, search_values, filter_by_prefix


@click.group(name="search")
def search_cmd() -> None:
    """Search and filter vault environment variables."""


@search_cmd.command("keys")
@click.argument("pattern")
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--key", "key_hex", default=None, help="Hex-encoded decryption key.")
@click.option("--regex", is_flag=True, default=False, help="Use regex instead of glob.")
@click.option("--case-sensitive", is_flag=True, default=False)
def search_keys_cmd(
    pattern: str,
    vault_path: str,
    key_hex: str | None,
    regex: bool,
    case_sensitive: bool,
) -> None:
    """Search for keys matching PATTERN."""
    key = bytes.fromhex(key_hex) if key_hex else None
    env = load_vault(vault_path, key=key)
    results = search_keys(env, pattern, use_regex=regex, case_sensitive=case_sensitive)
    if not results:
        click.echo("No matching keys found.")
        return
    for k, v in results.items():
        click.echo(f"{k}={v}")


@search_cmd.command("values")
@click.argument("pattern")
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--key", "key_hex", default=None, help="Hex-encoded decryption key.")
@click.option("--regex", is_flag=True, default=False)
@click.option("--case-sensitive", is_flag=True, default=False)
def search_values_cmd(
    pattern: str,
    vault_path: str,
    key_hex: str | None,
    regex: bool,
    case_sensitive: bool,
) -> None:
    """Search for entries whose values contain PATTERN."""
    key = bytes.fromhex(key_hex) if key_hex else None
    env = load_vault(vault_path, key=key)
    results = search_values(env, pattern, use_regex=regex, case_sensitive=case_sensitive)
    if not results:
        click.echo("No matching values found.")
        return
    for k, v in results.items():
        click.echo(f"{k}={v}")


@search_cmd.command("prefix")
@click.argument("prefix")
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--key", "key_hex", default=None)
def search_prefix_cmd(prefix: str, vault_path: str, key_hex: str | None) -> None:
    """List all keys starting with PREFIX."""
    key = bytes.fromhex(key_hex) if key_hex else None
    env = load_vault(vault_path, key=key)
    results = filter_by_prefix(env, prefix)
    if not results:
        click.echo(f"No keys with prefix '{prefix}'.")
        return
    for k, v in results.items():
        click.echo(f"{k}={v}")
