"""CLI commands for viewing and managing vault operation history."""

import click
from envault.history import (
    read_history,
    clear_history,
    list_projects_with_history,
)


@click.group("history")
def history_cmd():
    """View and manage vault operation history."""


@history_cmd.command("show")
@click.argument("project")
@click.option("--limit", "-n", default=20, show_default=True, help="Max entries to show.")
@click.option("--action", default=None, help="Filter by action type.")
def history_show(project: str, limit: int, action: str):
    """Show recent history for PROJECT."""
    entries = read_history(project, limit=limit, action_filter=action)
    if not entries:
        click.echo(f"No history found for project '{project}'.")
        return
    for entry in entries:
        ts = entry.get("timestamp", "?")
        act = entry.get("action", "?")
        details = entry.get("details", {})
        detail_str = ""
        if details:
            detail_str = "  " + "  ".join(f"{k}={v}" for k, v in details.items())
        click.echo(f"[{ts}] {act}{detail_str}")


@history_cmd.command("clear")
@click.argument("project")
@click.confirmation_option(prompt="Clear all history for this project?")
def history_clear(project: str):
    """Clear history for PROJECT."""
    deleted = clear_history(project)
    if deleted:
        click.echo(f"History cleared for '{project}'.")
    else:
        click.echo(f"No history found for '{project}'.")


@history_cmd.command("list")
def history_list():
    """List all projects that have recorded history."""
    projects = list_projects_with_history()
    if not projects:
        click.echo("No history records found.")
        return
    for name in projects:
        click.echo(name)
