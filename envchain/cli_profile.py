"""CLI commands for profile management."""

import click
from envchain.profile import (
    create_profile, load_profile, delete_profile,
    list_profiles, add_vault_to_profile, remove_vault_from_profile,
)


@click.group("profile")
def profile_cmd():
    """Manage vault profiles."""


@profile_cmd.command("create")
@click.argument("name")
@click.argument("vaults", nargs=-1)
def profile_create(name, vaults):
    """Create a new profile with optional initial vaults."""
    try:
        path = create_profile(name, list(vaults))
        click.echo(f"Profile '{name}' created at {path}.")
    except FileExistsError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@profile_cmd.command("delete")
@click.argument("name")
def profile_delete(name):
    """Delete a profile."""
    if delete_profile(name):
        click.echo(f"Profile '{name}' deleted.")
    else:
        click.echo(f"Profile '{name}' not found.", err=True)
        raise SystemExit(1)


@profile_cmd.command("list")
def profile_list():
    """List all profiles."""
    profiles = list_profiles()
    if not profiles:
        click.echo("No profiles found.")
    for p in profiles:
        click.echo(p)


@profile_cmd.command("show")
@click.argument("name")
def profile_show(name):
    """Show vaults in a profile."""
    try:
        data = load_profile(name)
        vaults = data.get("vaults", [])
        if not vaults:
            click.echo(f"Profile '{name}' has no vaults.")
        for v in vaults:
            click.echo(v)
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@profile_cmd.command("add-vault")
@click.argument("name")
@click.argument("vault")
def profile_add_vault(name, vault):
    """Add a vault to a profile."""
    try:
        add_vault_to_profile(name, vault)
        click.echo(f"Vault '{vault}' added to profile '{name}'.")
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@profile_cmd.command("remove-vault")
@click.argument("name")
@click.argument("vault")
def profile_remove_vault(name, vault):
    """Remove a vault from a profile."""
    try:
        if remove_vault_from_profile(name, vault):
            click.echo(f"Vault '{vault}' removed from profile '{name}'.")
        else:
            click.echo(f"Vault '{vault}' not in profile '{name}'.", err=True)
            raise SystemExit(1)
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
