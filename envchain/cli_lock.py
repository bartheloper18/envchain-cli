"""CLI commands for vault lock/unlock session management."""

import click
from envchain.lock import lock_vault, unlock_vault, is_unlocked, get_lock_info, DEFAULT_TIMEOUT
from envchain.audit import log_event
import time


@click.command("unlock")
@click.argument("vault_name")
@click.option("--timeout", default=DEFAULT_TIMEOUT, show_default=True, help="Session timeout in seconds.")
def unlock_cmd(vault_name: str, timeout: int) -> None:
    """Unlock a vault for a session window."""
    unlock_vault(vault_name, timeout=timeout)
    log_event(vault_name, "unlock", {"timeout": timeout})
    expires = time.time() + timeout
    click.echo(f"Vault '{vault_name}' unlocked for {timeout}s (expires at {int(expires)}).")


@click.command("lock")
@click.argument("vault_name")
def lock_cmd(vault_name: str) -> None:
    """Manually lock a vault, ending the session."""
    lock_vault(vault_name)
    log_event(vault_name, "lock", {})
    click.echo(f"Vault '{vault_name}' locked.")


@click.command("status")
@click.argument("vault_name")
def status_cmd(vault_name: str) -> None:
    """Show lock status of a vault."""
    info = get_lock_info(vault_name)
    if info is None:
        if is_unlocked(vault_name):
            click.echo(f"Vault '{vault_name}' is unlocked.")
        else:
            click.echo(f"Vault '{vault_name}' is locked or session expired.")
        return
    remaining = int(info["expires_at"] - time.time())
    click.echo(f"Vault '{vault_name}' is unlocked. Session expires in {remaining}s.")
