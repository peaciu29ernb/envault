"""CLI commands for type-checking env values."""
from __future__ import annotations

import json
from typing import Optional

import click

from envault.typecheck import infer_type, typecheck_env
from envault.vault import load_vault


@click.group(name="typecheck")
def typecheck_cmd() -> None:
    """Type-check env var values."""


@typecheck_cmd.command("infer")
@click.argument("vault_file")
@click.option("--key", "-k", "project", default=None, help="Keystore project name.")
@click.option("--password", "-p", default=None, help="Vault password.")
def typecheck_infer(vault_file: str, project: Optional[str], password: Optional[str]) -> None:
    """Infer types for all keys in VAULT_FILE and print them."""
    env = load_vault(vault_file, project=project, password=password)
    rows = [(k, infer_type(v)) for k, v in sorted(env.items())]
    width = max((len(k) for k, _ in rows), default=0)
    for k, t in rows:
        click.echo(f"{k:<{width}}  {t}")


@typecheck_cmd.command("check")
@click.argument("vault_file")
@click.argument("schema_file")
@click.option("--key", "-k", "project", default=None, help="Keystore project name.")
@click.option("--password", "-p", default=None, help="Vault password.")
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero on first violation.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output JSON.")
def typecheck_check(
    vault_file: str,
    schema_file: str,
    project: Optional[str],
    password: Optional[str],
    strict: bool,
    as_json: bool,
) -> None:
    """Check VAULT_FILE values against types declared in SCHEMA_FILE (JSON)."""
    env = load_vault(vault_file, project=project, password=password)
    with open(schema_file) as fh:
        schema = json.load(fh)
    violations = typecheck_env(env, schema, strict=False)
    if as_json:
        click.echo(json.dumps(violations, indent=2))
    else:
        if not violations:
            click.echo("All type checks passed.")
        else:
            for v in violations:
                click.echo(
                    f"  {v['key']}: expected {v['expected']}, "
                    f"inferred {v['inferred']} (value={v['actual_value']!r})"
                )
    if strict and violations:
        raise SystemExit(1)
