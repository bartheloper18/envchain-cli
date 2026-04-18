"""CLI commands for vault backup and restore."""

import click
from pathlib import Path

from envchain.backup import backup_vault, restore_vault, list_backups


@click.command("backup")
@click.argument("vault_name")
@click.option("--dest", default=None, help="Custom backup destination directory.")
def backup_cmd(vault_name: str, dest: str | None):
    """Backup a vault to a timestamped snapshot."""
    dest_path = Path(dest) if dest else None
    try:
        backup_path = backup_vault(vault_name, dest_path)
        click.echo(f"Vault '{vault_name}' backed up to: {backup_path}")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@click.command("restore")
@click.argument("backup_path")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing vault.")
def restore_cmd(backup_path: str, overwrite: bool):
    """Restore a vault from a backup snapshot."""
    path = Path(backup_path)
    try:
        vault_name = restore_vault(path, overwrite=overwrite)
        click.echo(f"Vault '{vault_name}' restored from: {path}")
    except (FileExistsError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@click.command("list-backups")
@click.argument("vault_name", required=False, default=None)
@click.option("--dest", default=None, help="Custom backup directory to search.")
def list_backups_cmd(vault_name: str | None, dest: str | None):
    """List available vault backups."""
    dest_path = Path(dest) if dest else None
    backups = list_backups(vault_name, dest_path)
    if not backups:
        click.echo("No backups found.")
    else:
        for b in backups:
            click.echo(str(b))
