"""CLI commands for signing and verifying vault env files."""

import click
from envault.vault import load_vault
from envault.signing import attach_signature, verify_signature, SIGNATURE_KEY
from envault.keystore import retrieve_key


@click.group(name="sign")
def signing_cmd():
    """Sign and verify env vault contents."""


@signing_cmd.command("attach")
@click.argument("vault_file")
@click.argument("project")
def sign_attach(vault_file: str, project: str):
    """Attach an HMAC signature to a decrypted vault and print the result."""
    try:
        secret = retrieve_key(project)
    except KeyError:
        click.echo(f"No key found for project '{project}'.", err=True)
        raise SystemExit(1)

    env = load_vault(vault_file, key=secret)
    signed = attach_signature(env, secret)
    for k, v in signed.items():
        click.echo(f"{k}={v}")


@signing_cmd.command("verify")
@click.argument("vault_file")
@click.argument("project")
def sign_verify(vault_file: str, project: str):
    """Verify the HMAC signature embedded in a vault."""
    try:
        secret = retrieve_key(project)
    except KeyError:
        click.echo(f"No key found for project '{project}'.", err=True)
        raise SystemExit(1)

    env = load_vault(vault_file, key=secret)

    if SIGNATURE_KEY not in env:
        click.echo("No signature found in vault.", err=True)
        raise SystemExit(2)

    if verify_signature(env, secret):
        click.echo("Signature valid. ✓")
    else:
        click.echo("Signature INVALID. ✗", err=True)
        raise SystemExit(3)
