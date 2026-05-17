"""CLI command: envault summarize — show statistics for an encrypted vault."""

from __future__ import annotations

import json

import click

from envault.vault import load_vault
from envault.summarize import summarize


@click.group("summarize")
def summarize_cmd() -> None:
    """Show statistics for a vault's env contents."""


@summarize_cmd.command("run")
@click.argument("vault_path")
@click.option("--key", "key_hex", default=None, help="Hex-encoded decryption key.")
@click.option(
    "--format",
    "fmt",
    default="text",
    type=click.Choice(["text", "json"]),
    show_default=True,
    help="Output format.",
)
def summarize_run(vault_path: str, key_hex: str | None, fmt: str) -> None:
    """Decrypt VAULT_PATH and print a summary of its contents."""
    key: bytes | None = bytes.fromhex(key_hex) if key_hex else None

    try:
        env = load_vault(vault_path, key=key)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    report = summarize(env)

    if fmt == "json":
        click.echo(json.dumps(report, indent=2))
    else:
        click.echo(f"Total keys        : {report['total_keys']}")
        click.echo(f"Non-empty values  : {report['non_empty_values']}")
        click.echo(f"Empty values      : {report['empty_values']}")
        click.echo(f"Sensitive keys    : {report['sensitive_keys']}")
        click.echo(f"Avg value length  : {report['average_value_length']}")
        click.echo(f"Longest key       : {report['longest_key']}")
