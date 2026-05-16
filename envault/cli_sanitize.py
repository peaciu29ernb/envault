"""cli_sanitize.py — CLI commands for sanitizing vault env values."""

import json
import click
from envault.vault import load_vault, save_vault
from envault.sanitize import sanitize_env, list_sanitizers, SanitizeError


@click.group("sanitize")
def sanitize_cmd() -> None:
    """Sanitize env variable values in a vault."""


@sanitize_cmd.command("run")
@click.argument("vault_file")
@click.option(
    "-s",
    "--sanitizer",
    "sanitizers",
    multiple=True,
    required=True,
    help="Sanitizer(s) to apply (can repeat).",
)
@click.option(
    "-k",
    "--key",
    "keys",
    multiple=True,
    default=None,
    help="Only sanitize these keys (default: all).",
)
@click.option("--key-name", default=None, help="Keystore project name for decryption.")
@click.option("--dry-run", is_flag=True, help="Print result without saving.")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def sanitize_run(
    vault_file: str,
    sanitizers: tuple,
    keys: tuple,
    key_name: str,
    dry_run: bool,
    as_json: bool,
) -> None:
    """Apply sanitizers to values in VAULT_FILE."""
    try:
        env = load_vault(vault_file, key_name=key_name)
        result = sanitize_env(env, list(sanitizers), list(keys) if keys else None)
    except SanitizeError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(result, indent=2))
        return

    if dry_run:
        for k, v in result.items():
            click.echo(f"{k}={v}")
        return

    save_vault(vault_file, result, key_name=key_name)
    click.echo(f"Sanitized {len(result)} key(s) and saved to {vault_file}.")


@sanitize_cmd.command("list")
def sanitize_list() -> None:
    """List available sanitizer names."""
    for name in list_sanitizers():
        click.echo(name)
