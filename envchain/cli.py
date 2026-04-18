"""CLI entry point for envchain."""

import click
import os

from envchain.vault import create_vault, load_vault, save_vault
from envchain.shell import detect_shell, format_exports, inject_into_env
from envchain.audit import log_event, read_events, format_events

VAULT_DIR = os.environ.get("ENVCHAIN_DIR", os.path.expanduser("~/.envchain"))


@click.group()
def cli():
    """envchain — manage encrypted environment variable vaults."""
    os.makedirs(VAULT_DIR, exist_ok=True)


@cli.command()
@click.argument("name")
@click.password_option(prompt="Vault password")
def new_vault(name, password):
    """Create a new encrypted vault."""
    create_vault(VAULT_DIR, name, password)
    log_event(VAULT_DIR, name, "CREATE")
    click.echo(f"Vault '{name}' created.")


@cli.command()
@click.argument("vault")
@click.argument("key")
@click.argument("value")
@click.password_option(prompt="Vault password")
def set_var(vault, key, value, password):
    """Set an environment variable in a vault."""
    data = load_vault(VAULT_DIR, vault, password)
    data[key] = value
    save_vault(VAULT_DIR, vault, password, data)
    log_event(VAULT_DIR, vault, "SET", key)
    click.echo(f"Set {key} in vault '{vault}'.")


@cli.command()
@click.argument("vault")
@click.argument("key")
@click.password_option(prompt="Vault password")
def get_var(vault, key, password):
    """Get an environment variable from a vault."""
    data = load_vault(VAULT_DIR, vault, password)
    log_event(VAULT_DIR, vault, "GET", key)
    if key not in data:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
    click.echo(data[key])


@cli.command()
@click.argument("vault")
@click.password_option(prompt="Vault password")
def list_all(vault, password):
    """List all variable names in a vault."""
    data = load_vault(VAULT_DIR, vault, password)
    log_event(VAULT_DIR, vault, "LIST")
    for key in data:
        click.echo(key)


@cli.command()
@click.argument("vault")
@click.option("--vault-name", default=None, help="Filter by vault name.")
def audit(vault, vault_name):
    """Show audit log for vaults."""
    events = read_events(VAULT_DIR, vault_name=vault_name or vault)
    click.echo(format_events(events))
