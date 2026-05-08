"""CLI commands for env validation against a schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from envault.validate import load_schema, validate_env
from envault.vault import load_vault


@click.group("validate")
def validate_cmd():
    """Validate decrypted env variables against a schema."""


@validate_cmd.command("run")
@click.argument("vault_file", default=".env.vault")
@click.option("--schema", "schema_path", default=".env.schema.json", show_default=True,
              help="Path to JSON schema file.")
@click.option("--key", "key_hex", default=None, help="Hex-encoded encryption key.")
@click.option("--password", default=None, help="Password used to encrypt the vault.")
@click.option("--project", default=None, help="Project name to look up key in keystore.")
@click.option("--output", type=click.Choice(["text", "json"]), default="text", show_default=True)
def validate_run(
    vault_file: str,
    schema_path: str,
    key_hex: str | None,
    password: str | None,
    project: str | None,
    output: str,
):
    """Decrypt a vault and validate its contents against a JSON schema."""
    # Resolve key
    key: bytes | None = None
    if key_hex:
        key = bytes.fromhex(key_hex)
    elif project:
        from envault.keystore import retrieve_key
        key = retrieve_key(project)

    try:
        env = load_vault(vault_file, key=key, password=password)
    except Exception as exc:
        click.echo(f"Error loading vault: {exc}", err=True)
        sys.exit(1)

    try:
        schema = load_schema(schema_path)
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)

    result = validate_env(env, schema)

    if output == "json":
        issues = [i.to_dict() for i in result.all_issues()]
        click.echo(json.dumps({"ok": result.ok, "issues": issues}, indent=2))
    else:
        if not result.all_issues():
            click.echo("✓ All validations passed.")
        else:
            for issue in result.all_issues():
                click.echo(repr(issue))

    if not result.ok:
        sys.exit(1)
