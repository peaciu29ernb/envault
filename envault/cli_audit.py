"""CLI commands for viewing and managing the envault audit log."""

import click
from pathlib import Path
from typing import Optional

from envault.audit import read_events, clear_events


@click.group("audit")
def audit_cmd():
    """Manage the envault audit log."""


@audit_cmd.command("show")
@click.option("--project", "-p", default=None, help="Filter events by project name.")
@click.option(
    "--log",
    default=None,
    type=click.Path(),
    help="Path to audit log file.",
)
def show_audit(project: Optional[str], log: Optional[str]):
    """Display audit log events."""
    log_path = Path(log) if log else None
    events = read_events(project=project, log_path=log_path)

    if not events:
        click.echo("No audit events found.")
        return

    for event in events:
        line = "[{timestamp}] {action:10s} project={project}".format(**event)
        if event.get("details"):
            line += f"  ({event['details']})"
        click.echo(line)


@audit_cmd.command("clear")
@click.option(
    "--log",
    default=None,
    type=click.Path(),
    help="Path to audit log file.",
)
@click.confirmation_option(prompt="Are you sure you want to clear the audit log?")
def clear_audit(log: Optional[str]):
    """Clear all audit log events."""
    log_path = Path(log) if log else None
    count = clear_events(log_path=log_path)
    click.echo(f"Cleared {count} audit event(s).")
