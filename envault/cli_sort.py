"""CLI commands for sorting .env keys."""

from __future__ import annotations

import click

from envault.sort import SortError, sort_env
from envault.vault import load_vault, save_vault


@click.group("sort", help="Sort keys in a vault file.")
def sort_cmd() -> None:  # pragma: no cover
    pass


@sort_cmd.command("run")
@click.argument("vault_file")
@click.option(
    "--strategy",
    default="alpha",
    show_default=True,
    type=click.Choice(["alpha", "key_length", "value_length", "custom"]),
    help="Sort strategy to apply.",
)
@click.option("--reverse", is_flag=True, default=False, help="Reverse the sort order.")
@click.option(
    "--order",
    default=None,
    help="Comma-separated key order for the 'custom' strategy.",
)
@click.option("--key", default=None, help="Decryption key (hex). Reads from keystore if omitted.")
@click.option("--dry-run", is_flag=True, default=False, help="Print result without saving.")
def sort_run(
    vault_file: str,
    strategy: str,
    reverse: bool,
    order: str | None,
    key: str | None,
    dry_run: bool,
) -> None:
    """Sort the keys of VAULT_FILE and write the result back."""
    try:
        raw_key = bytes.fromhex(key) if key else None
        env = load_vault(vault_file, key=raw_key)

        order_list = [k.strip() for k in order.split(",")] if order else None
        sorted_env = sort_env(env, strategy=strategy, reverse=reverse, order=order_list)

        if dry_run:
            for k, v in sorted_env.items():
                click.echo(f"{k}={v}")
        else:
            save_vault(vault_file, sorted_env, key=raw_key)
            click.echo(f"Sorted {len(sorted_env)} key(s) using strategy '{strategy}'.")

    except SortError as exc:
        raise click.ClickException(str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc
