"""CLI commands for managing vault variable aliases."""

import click
from envchain.alias import add_alias, remove_alias, resolve_alias, list_aliases

DEFAULT_DIR = click.get_app_dir("envchain")


@click.group("alias")
def alias_cmd():
    """Manage short-name aliases for vault variables."""


@alias_cmd.command("add")
@click.argument("alias")
@click.argument("vault")
@click.argument("key")
@click.option("--dir", "base_dir", default=DEFAULT_DIR, hidden=True)
def alias_add(alias, vault, key, base_dir):
    """Add an alias NAME pointing to VAULT:KEY."""
    try:
        add_alias(base_dir, alias, vault, key)
        click.echo(f"Alias '{alias}' -> {vault}:{key} added.")
    except ValueError as e:
        raise click.ClickException(str(e))


@alias_cmd.command("remove")
@click.argument("alias")
@click.option("--dir", "base_dir", default=DEFAULT_DIR, hidden=True)
def alias_remove(alias, base_dir):
    """Remove an alias by name."""
    removed = remove_alias(base_dir, alias)
    if removed:
        click.echo(f"Alias '{alias}' removed.")
    else:
        raise click.ClickException(f"Alias '{alias}' not found.")


@alias_cmd.command("resolve")
@click.argument("alias")
@click.option("--dir", "base_dir", default=DEFAULT_DIR, hidden=True)
def alias_resolve(alias, base_dir):
    """Show the vault:key target for an alias."""
    result = resolve_alias(base_dir, alias)
    if result is None:
        raise click.ClickException(f"Alias '{alias}' not found.")
    click.echo(f"{result['vault']}:{result['key']}")


@alias_cmd.command("list")
@click.option("--dir", "base_dir", default=DEFAULT_DIR, hidden=True)
def alias_list(base_dir):
    """List all defined aliases."""
    entries = list_aliases(base_dir)
    if not entries:
        click.echo("No aliases defined.")
        return
    for entry in entries:
        click.echo(f"{entry['alias']:20s}  {entry['vault']}:{entry['key']}")
