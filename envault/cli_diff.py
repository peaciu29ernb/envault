"""CLI commands for diffing two encrypted vault files."""

import click
from envault.vault import load_vault
from envault.diff import diff_envs, format_diff, has_changes
from envault.keystore import retrieve_key


@click.group("diff")
def diff_cmd():
    """Commands for comparing vault contents."""


@diff_cmd.command("run")
@click.argument("vault_a", type=click.Path(exists=True))
@click.argument("vault_b", type=click.Path(exists=True))
@click.option("--project", "-p", default=None, help="Project name for key lookup.")
@click.option("--key-a", default=None, help="Hex key for vault_a (overrides keystore).")
@click.option("--key-b", default=None, help="Hex key for vault_b (overrides keystore).")
@click.option("--show-values", is_flag=True, default=False, help="Show actual values in diff output.")
def diff_run(vault_a, vault_b, project, key_a, key_b, show_values):
    """Diff two vault files and print the result."""
    try:
        if key_a:
            raw_a = bytes.fromhex(key_a)
        elif project:
            raw_a = retrieve_key(project)
        else:
            raise click.UsageError("Provide --project or --key-a to decrypt vault_a.")

        if key_b:
            raw_b = bytes.fromhex(key_b)
        elif project:
            raw_b = raw_a
        else:
            raise click.UsageError("Provide --project or --key-b to decrypt vault_b.")

        env_a = load_vault(vault_a, key=raw_a)
        env_b = load_vault(vault_b, key=raw_b)

    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    diff = diff_envs(env_a, env_b)

    if not has_changes(diff):
        click.echo("No differences found.")
        return

    summary = (
        f"+{len(diff['added'])} added  "
        f"-{len(diff['removed'])} removed  "
        f"~{len(diff['changed'])} changed  "
        f"={len(diff['unchanged'])} unchanged"
    )
    click.echo(summary)
    click.echo(format_diff(diff, show_values=show_values))
