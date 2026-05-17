"""CLI commands for filtering env variables."""

from __future__ import annotations

import json

import click

from envault.filter import FilterError, filter_env
from envault.vault import load_vault


@click.group(name="filter")
def filter_cmd() -> None:
    """Filter variables from a vault."""


@filter_cmd.command(name="run")
@click.argument("vault_path")
@click.option("--key", "include_keys", multiple=True, help="Include only these keys.")
@click.option("--exclude", "exclude_keys", multiple=True, help="Exclude these keys.")
@click.option("--glob", default=None, help="Keep keys matching this glob pattern.")
@click.option("--regex", default=None, help="Keep keys matching this regex pattern.")
@click.option("--non-empty", is_flag=True, default=False, help="Drop keys with empty values.")
@click.option("--format", "fmt", type=click.Choice(["env", "json"]), default="env")
@click.option("--password", default=None, envvar="ENVAULT_PASSWORD", help="Vault password.")
def filter_run(
    vault_path: str,
    include_keys: tuple,
    exclude_keys: tuple,
    glob: str | None,
    regex: str | None,
    non_empty: bool,
    fmt: str,
    password: str | None,
) -> None:
    """Filter variables from VAULT_PATH and print results."""
    try:
        env = load_vault(vault_path, password=password)
    except Exception as exc:  # pragma: no cover
        raise click.ClickException(str(exc)) from exc

    try:
        result = filter_env(
            env,
            include_keys=list(include_keys) if include_keys else None,
            exclude_keys=list(exclude_keys) if exclude_keys else None,
            glob=glob,
            regex=regex,
            non_empty=non_empty,
        )
    except FilterError as exc:
        raise click.ClickException(str(exc)) from exc

    if fmt == "json":
        click.echo(json.dumps(result, indent=2))
    else:
        for k, v in result.items():
            click.echo(f"{k}={v}")
