"""CLI commands for managing envault notification channels and hooks."""

from __future__ import annotations

import click

from envault.notify import add_channel, fire, list_channels, remove_channel


@click.group(name="notify")
def notify_cmd() -> None:
    """Manage notification channels and fire test events."""


@notify_cmd.command("add")
@click.argument("channel")
@click.option("--base-dir", default=None, hidden=True)
def notify_add(channel: str, base_dir: str | None) -> None:
    """Register a notification channel."""
    add_channel(channel, base_dir=base_dir)
    click.echo(f"Channel '{channel}' added.")
    channels = list_channels(base_dir=base_dir)
    click.echo("Channels: " + ", ".join(channels))


@notify_cmd.command("remove")
@click.argument("channel")
@click.option("--base-dir", default=None, hidden=True)
def notify_remove(channel: str, base_dir: str | None) -> None:
    """Remove a notification channel."""
    removed = remove_channel(channel, base_dir=base_dir)
    if removed:
        click.echo(f"Channel '{channel}' removed.")
    else:
        click.echo(f"Channel '{channel}' not found.", err=True)
        raise SystemExit(1)


@notify_cmd.command("list")
@click.option("--base-dir", default=None, hidden=True)
def notify_list(base_dir: str | None) -> None:
    """List all registered notification channels."""
    channels = list_channels(base_dir=base_dir)
    if not channels:
        click.echo("No channels registered.")
    else:
        for ch in channels:
            click.echo(f"  - {ch}")


@notify_cmd.command("fire")
@click.argument("event")
@click.option("--project", default="", help="Project name to include in payload.")
def notify_fire(event: str, project: str) -> None:
    """Fire a named event and invoke any registered in-process hooks."""
    payload = {"event": event, "project": project}
    outcomes = fire(event, payload)
    if not outcomes:
        click.echo(f"Event '{event}' fired (no hooks registered).")
    else:
        for i, result in enumerate(outcomes, 1):
            click.echo(f"  Hook {i}: {result}")
