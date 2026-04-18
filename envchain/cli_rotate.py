"""CLI commands for vault password rotation."""

import click
from envchain.rotate import rotate_password, rotate_all, verify_password
from envchain.vault import load_vault
from envchain.audit import log_event


@click.command("rotate")
@click.argument("vault_name")
@click.option("--old-password", prompt=True, hide_input=True, help="Current vault password")
@click.option("--new-password", prompt=True, hide_input=True, confirmation_prompt=True, help="New vault password")
def rotate_cmd(vault_name: str, old_password: str, new_password: str):
    """Rotate the password for a vault."""
    try:
        rotate_password(vault_name, old_password, new_password)
        log_event(vault_name, "rotate", {"status": "success"})
        click.echo(f"Password rotated successfully for vault '{vault_name}'.")
    except FileNotFoundError:
        click.echo(f"Error: Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error rotating password: {e}", err=True)
        raise SystemExit(1)


@click.command("verify")
@click.argument("vault_name")
@click.option("--password", prompt=True, hide_input=True, help="Password to verify")
def verify_cmd(vault_name: str, password: str):
    """Verify that a password is correct for a vault."""
    if verify_password(vault_name, password):
        click.echo(f"Password is correct for vault '{vault_name}'.")
    else:
        click.echo(f"Incorrect password for vault '{vault_name}'.", err=True)
        raise SystemExit(1)
