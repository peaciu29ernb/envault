"""CLI commands for managing per-project key access control."""

from __future__ import annotations

import click
from envault.access import (
    grant_access,
    revoke_access,
    get_accessible_keys,
    can_access,
    list_roles,
    delete_role,
)


@click.group("access")
def access_cmd() -> None:
    """Manage role-based key access control."""


@access_cmd.command("grant")
@click.argument("project")
@click.argument("role")
@click.argument("key")
def access_grant(project: str, role: str, key: str) -> None:
    """Grant ROLE access to KEY in PROJECT."""
    keys = grant_access(project, role, key)
    click.echo(f"Granted '{role}' access to '{key}'. Accessible keys: {', '.join(keys)}")


@access_cmd.command("revoke")
@click.argument("project")
@click.argument("role")
@click.argument("key")
def access_revoke(project: str, role: str, key: str) -> None:
    """Revoke ROLE's access to KEY in PROJECT."""
    removed = revoke_access(project, role, key)
    if removed:
        click.echo(f"Revoked '{role}' access to '{key}'.")
    else:
        click.echo(f"'{role}' did not have access to '{key}'.")


@access_cmd.command("list")
@click.argument("project")
@click.argument("role")
def access_list(project: str, role: str) -> None:
    """List keys accessible by ROLE in PROJECT."""
    keys = get_accessible_keys(project, role)
    if keys:
        for k in keys:
            click.echo(k)
    else:
        click.echo(f"No keys accessible by '{role}'.")


@access_cmd.command("check")
@click.argument("project")
@click.argument("role")
@click.argument("key")
def access_check(project: str, role: str, key: str) -> None:
    """Check whether ROLE can access KEY in PROJECT."""
    if can_access(project, role, key):
        click.echo(f"'{role}' CAN access '{key}'.")
    else:
        click.echo(f"'{role}' CANNOT access '{key}'.")


@access_cmd.command("roles")
@click.argument("project")
def access_roles(project: str) -> None:
    """List all roles with access entries in PROJECT."""
    roles = list_roles(project)
    if roles:
        for r in roles:
            click.echo(r)
    else:
        click.echo("No roles defined.")


@access_cmd.command("delete-role")
@click.argument("project")
@click.argument("role")
def access_delete_role(project: str, role: str) -> None:
    """Delete all access entries for ROLE in PROJECT."""
    removed = delete_role(project, role)
    if removed:
        click.echo(f"Deleted role '{role}' from project '{project}'.")
    else:
        click.echo(f"Role '{role}' not found in project '{project}'.")
