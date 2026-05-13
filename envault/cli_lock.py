"""CLI commands for key locking."""

import click
from pathlib import Path
from envault.lock import lock_key, unlock_key, get_locks, is_locked


@click.group(name="lock")
def lock_cmd():
    """Lock or unlock env keys to prevent accidental modification."""


@lock_cmd.command("add")
@click.argument("project")
@click.argument("key")
@click.option("--base-dir", default=None, help="Override lock storage directory.")
def lock_add(project: str, key: str, base_dir: str):
    """Lock KEY in PROJECT."""
    bd = Path(base_dir) if base_dir else None
    kwargs = {"base_dir": bd} if bd else {}
    locks = lock_key(project, key, **kwargs)
    click.echo(f"Locked '{key}' in project '{project}'.")
    click.echo(f"Locked keys: {', '.join(locks) if locks else '(none)'}")


@lock_cmd.command("remove")
@click.argument("project")
@click.argument("key")
@click.option("--base-dir", default=None, help="Override lock storage directory.")
def lock_remove(project: str, key: str, base_dir: str):
    """Unlock KEY in PROJECT."""
    bd = Path(base_dir) if base_dir else None
    kwargs = {"base_dir": bd} if bd else {}
    removed = unlock_key(project, key, **kwargs)
    if removed:
        click.echo(f"Unlocked '{key}' in project '{project}'.")
    else:
        click.echo(f"Key '{key}' was not locked in project '{project}'.")


@lock_cmd.command("list")
@click.argument("project")
@click.option("--base-dir", default=None, help="Override lock storage directory.")
def lock_list(project: str, base_dir: str):
    """List all locked keys for PROJECT."""
    bd = Path(base_dir) if base_dir else None
    kwargs = {"base_dir": bd} if bd else {}
    locks = get_locks(project, **kwargs)
    if not locks:
        click.echo(f"No locked keys for project '{project}'.")
    else:
        click.echo(f"Locked keys for '{project}':")
        for k in locks:
            click.echo(f"  - {k}")


@lock_cmd.command("check")
@click.argument("project")
@click.argument("key")
@click.option("--base-dir", default=None, help="Override lock storage directory.")
def lock_check(project: str, key: str, base_dir: str):
    """Check whether KEY is locked in PROJECT."""
    bd = Path(base_dir) if base_dir else None
    kwargs = {"base_dir": bd} if bd else {}
    locked = is_locked(project, key, **kwargs)
    status = "LOCKED" if locked else "unlocked"
    click.echo(f"Key '{key}' in project '{project}': {status}")
