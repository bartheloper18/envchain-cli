"""CLI entry point for envchain using Click."""

import click
from envchain.vault import create_vault, load_vault, save_vault, list_vaults


@click.group()
def cli():
    """envchain — manage and inject encrypted environment variable vaults."""
    pass


@cli.command("new")
@click.argument("vault_name")
def new_vault(vault_name):
    """Create a new empty vault."""
    try:
        path = create_vault(vault_name)
        click.echo(f"Vault '{vault_name}' created at {path}")
    except FileExistsError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@cli.command("set")
@click.argument("vault_name")
@click.argument("key")
@click.argument("value")
def set_var(vault_name, key, value):
    """Set an environment variable in a vault."""
    try:
        data = load_vault(vault_name)
        data[key] = value
        save_vault(vault_name, data)
        click.echo(f"Set '{key}' in vault '{vault_name}'.")
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@cli.command("get")
@click.argument("vault_name")
@click.argument("key")
def get_var(vault_name, key):
    """Get an environment variable from a vault."""
    try:
        data = load_vault(vault_name)
        if key not in data:
            click.echo(f"Key '{key}' not found in vault '{vault_name}'.", err=True)
            raise SystemExit(1)
        click.echo(data[key])
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@cli.command("list")
def list_all():
    """List all available vaults."""
    vaults = list_vaults()
    if not vaults:
        click.echo("No vaults found.")
    else:
        for v in vaults:
            click.echo(v)


if __name__ == "__main__":
    cli()
