"""CLI commands for the clone feature."""

from __future__ import annotations

import json

import click

from envault.clone import CloneError, clone_env, clone_report
from envault.vault import load_vault, save_vault


@click.group(name="clone")
def clone_cmd() -> None:
    """Clone / copy env entries between vaults."""


@clone_cmd.command(name="run")
@click.argument("src")
@click.argument("dst")
@click.option("--key", "keys", multiple=True, help="Keys to include (repeatable).")
@click.option("--exclude", "excludes", multiple=True, help="Keys to drop (repeatable).")
@click.option("--prefix", default=None, help="Only copy keys with this prefix.")
@click.option("--strip-prefix", is_flag=True, default=False, help="Remove prefix from copied keys.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys in DST.")
@click.option("--dry-run", is_flag=True, default=False, help="Print result without writing.")
@click.option("--report", is_flag=True, default=False, help="Print a JSON clone report.")
def clone_run(
    src: str,
    dst: str,
    keys: tuple,
    excludes: tuple,
    prefix: str | None,
    strip_prefix: bool,
    overwrite: bool,
    dry_run: bool,
    report: bool,
) -> None:
    """Clone entries from SRC vault into DST vault."""
    src_env, src_meta = load_vault(src)
    dst_env, dst_meta = load_vault(dst)

    try:
        cloned = clone_env(
            src_env,
            include=list(keys) if keys else None,
            exclude=set(excludes) if excludes else None,
            prefix=prefix,
            strip_prefix=strip_prefix,
        )
    except CloneError as exc:
        raise click.ClickException(str(exc)) from exc

    if report:
        click.echo(json.dumps(clone_report(src_env, cloned), indent=2))

    merged = dict(dst_env)
    for k, v in cloned.items():
        if k in merged and not overwrite:
            click.echo(f"Skipping existing key '{k}' (use --overwrite to replace).")
            continue
        merged[k] = v

    if dry_run:
        click.echo(json.dumps(merged, indent=2))
        return

    save_vault(dst, merged, dst_meta.get("key"), password=dst_meta.get("password"))
    click.echo(f"Cloned {len(cloned)} key(s) from '{src}' into '{dst}'.")
