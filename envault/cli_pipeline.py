"""CLI commands for running and inspecting env pipelines."""

import json

import click

from envault.pipeline import Pipeline, build_pipeline
from envault.vault import load_vault
from envault.transform import apply_transform


@click.group("pipeline")
def pipeline_cmd():
    """Chain and run env transformation pipelines."""


@pipeline_cmd.command("run")
@click.argument("vault_file")
@click.option("--key", "key_hex", envvar="ENVAULT_KEY", required=True, help="Hex-encoded vault key")
@click.option("--step", "steps", multiple=True, metavar="NAME:TRANSFORM",
              help="Step in NAME:TRANSFORM format, e.g. upcase:upper. Repeatable.")
@click.option("--output", type=click.Choice(["env", "json"]), default="env", show_default=True)
def pipeline_run(vault_file: str, key_hex: str, steps: tuple, output: str):
    """Decrypt VAULT_FILE and run a pipeline of transforms on its contents."""
    try:
        key = bytes.fromhex(key_hex)
    except ValueError:
        raise click.ClickException("--key must be a valid hex string")

    try:
        env = load_vault(vault_file, key=key)
    except Exception as exc:
        raise click.ClickException(f"Failed to load vault: {exc}")

    pipeline = Pipeline(name="cli-pipeline")
    for raw in steps:
        if ":" not in raw:
            raise click.ClickException(f"Invalid step format '{raw}', expected NAME:TRANSFORM")
        step_name, transform = raw.split(":", 1)
        t = transform  # capture
        pipeline.add_step(step_name, lambda d, _t=t: {k: apply_transform(v, _t) for k, v in d.items()})

    try:
        result = pipeline.run(env)
    except Exception as exc:
        raise click.ClickException(str(exc))

    if output == "json":
        click.echo(json.dumps(result, indent=2))
    else:
        for k, v in result.items():
            click.echo(f"{k}={v}")


@pipeline_cmd.command("list-steps")
@click.option("--step", "steps", multiple=True, metavar="NAME:TRANSFORM")
def pipeline_list_steps(steps: tuple):
    """Print the ordered steps that would be executed."""
    if not steps:
        click.echo("No steps defined.")
        return
    click.echo("Pipeline steps:")
    for i, raw in enumerate(steps, 1):
        name = raw.split(":", 1)[0] if ":" in raw else raw
        transform = raw.split(":", 1)[1] if ":" in raw else "(invalid)"
        click.echo(f"  {i}. {name!r} -> transform={transform!r}")
