"""CLI commands for splitting an env vault into named partitions."""

from __future__ import annotations

import json
from typing import Optional

import click

from envault.split import SplitError, split_by_glob, split_by_prefix, split_by_regex
from envault.vault import load_vault


@click.group("split")
def split_cmd() -> None:
    """Split a vault into named partitions."""


@split_cmd.command("prefix")
@click.argument("vault_file")
@click.argument("prefixes", nargs=-1, required=True)
@click.option("--strip", is_flag=True, default=False, help="Strip prefix from output keys.")
@click.option("--no-rest", is_flag=True, default=False, help="Omit unmatched keys.")
@click.option("--key", "vault_key", default=None, help="Decryption key (hex).")
def split_prefix(
    vault_file: str,
    prefixes: tuple,
    strip: bool,
    no_rest: bool,
    vault_key: Optional[str],
) -> None:
    """Split vault by key prefixes."""
    _key = bytes.fromhex(vault_key) if vault_key else None
    try:
        env = load_vault(vault_file, key=_key)
    except Exception as exc:  # pragma: no cover
        raise click.ClickException(str(exc)) from exc

    remainder = None if no_rest else "__rest__"
    result = split_by_prefix(env, list(prefixes), remainder_key=remainder, strip_prefix=strip)
    click.echo(json.dumps(result, indent=2))


@split_cmd.command("glob")
@click.argument("vault_file")
@click.option("-p", "--pattern", "patterns", multiple=True, metavar="NAME=GLOB",
              help="Bucket pattern as NAME=GLOB.")
@click.option("--no-rest", is_flag=True, default=False)
@click.option("--key", "vault_key", default=None)
def split_glob(
    vault_file: str,
    patterns: tuple,
    no_rest: bool,
    vault_key: Optional[str],
) -> None:
    """Split vault by glob patterns."""
    pat_dict = _parse_kv_patterns(patterns)
    _key = bytes.fromhex(vault_key) if vault_key else None
    try:
        env = load_vault(vault_file, key=_key)
    except Exception as exc:  # pragma: no cover
        raise click.ClickException(str(exc)) from exc

    remainder = None if no_rest else "__rest__"
    try:
        result = split_by_glob(env, pat_dict, remainder_key=remainder)
    except SplitError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, indent=2))


@split_cmd.command("regex")
@click.argument("vault_file")
@click.option("-p", "--pattern", "patterns", multiple=True, metavar="NAME=REGEX")
@click.option("--no-rest", is_flag=True, default=False)
@click.option("--key", "vault_key", default=None)
def split_regex(
    vault_file: str,
    patterns: tuple,
    no_rest: bool,
    vault_key: Optional[str],
) -> None:
    """Split vault by regex patterns."""
    pat_dict = _parse_kv_patterns(patterns)
    _key = bytes.fromhex(vault_key) if vault_key else None
    try:
        env = load_vault(vault_file, key=_key)
    except Exception as exc:  # pragma: no cover
        raise click.ClickException(str(exc)) from exc

    remainder = None if no_rest else "__rest__"
    try:
        result = split_by_regex(env, pat_dict, remainder_key=remainder)
    except SplitError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, indent=2))


def _parse_kv_patterns(patterns: tuple) -> dict:
    result = {}
    for item in patterns:
        if "=" not in item:
            raise click.ClickException(f"Pattern must be NAME=VALUE, got: {item!r}")
        name, _, value = item.partition("=")
        result[name.strip()] = value.strip()
    return result
