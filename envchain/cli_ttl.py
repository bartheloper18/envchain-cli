"""CLI commands for managing secret TTLs."""
import click
from envchain.ttl import set_ttl, remove_ttl, get_ttl_info, purge_expired, is_expired


@click.command("set-ttl")
@click.argument("vault_name")
@click.argument("key")
@click.argument("seconds", type=int)
def set_ttl_cmd(vault_name: str, key: str, seconds: int) -> None:
    """Set a TTL (in seconds) for a key in a vault."""
    set_ttl(vault_name, key, seconds)
    click.echo(f"TTL of {seconds}s set for '{key}' in vault '{vault_name}'.")


@click.command("remove-ttl")
@click.argument("vault_name")
@click.argument("key")
def remove_ttl_cmd(vault_name: str, key: str) -> None:
    """Remove the TTL for a key in a vault."""
    remove_ttl(vault_name, key)
    click.echo(f"TTL removed for '{key}' in vault '{vault_name}'.")


@click.command("ttl-status")
@click.argument("vault_name")
@click.argument("key")
def ttl_status_cmd(vault_name: str, key: str) -> None:
    """Show TTL status for a key."""
    info = get_ttl_info(vault_name, key)
    if info is None:
        click.echo(f"No TTL set for '{key}' in vault '{vault_name}'.")
        return
    expired = is_expired(vault_name, key)
    status = "EXPIRED" if expired else "active"
    click.echo(f"Key: {key} | Status: {status} | Remaining: {info['remaining']:.1f}s / {info['ttl']}s")


@click.command("purge-expired")
@click.argument("vault_name")
def purge_expired_cmd(vault_name: str) -> None:
    """Purge all expired TTL entries for a vault."""
    removed = purge_expired(vault_name)
    if removed:
        click.echo(f"Purged expired keys: {', '.join(removed)}")
    else:
        click.echo("No expired keys found.")
