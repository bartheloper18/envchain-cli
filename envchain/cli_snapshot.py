"""CLI commands for vault snapshot management."""

import click
from pathlib import Path
from datetime import datetime

from envchain.snapshot import create_snapshot, restore_snapshot, list_snapshots


@click.command("snapshot-create")
@click.argument("label")
@click.argument("vaults", nargs=-1, required=True)
@click.option("--password", prompt=True, hide_input=True, help="Master password for the vaults.")
def snapshot_create_cmd(label: str, vaults: tuple, password: str) -> None:
    """Create a snapshot of one or more vaults under LABEL."""
    try:
        path = create_snapshot(label, list(vaults), password)
        click.echo(f"Snapshot '{label}' created: {path}")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Failed to create snapshot: {e}", err=True)
        raise SystemExit(1)


@click.command("snapshot-restore")
@click.argument("snapshot_file", type=click.Path(exists=True))
@click.option("--password", prompt=True, hide_input=True, help="Password used when snapshot was created.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing vaults.")
def snapshot_restore_cmd(snapshot_file: str, password: str, overwrite: bool) -> None:
    """Restore vaults from SNAPSHOT_FILE."""
    try:
        restored = restore_snapshot(Path(snapshot_file), password, overwrite=overwrite)
        click.echo(f"Restored vaults: {', '.join(restored)}")
    except FileExistsError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Failed to restore snapshot: {e}", err=True)
        raise SystemExit(1)


@click.command("snapshot-list")
def snapshot_list_cmd() -> None:
    """List all available snapshots."""
    snapshots = list_snapshots()
    if not snapshots:
        click.echo("No snapshots found.")
        return
    click.echo(f"{'Label':<30} {'Created':<22} {'File'}")
    click.echo("-" * 72)
    for snap in snapshots:
        ts = datetime.fromtimestamp(snap["created_at"]).strftime("%Y-%m-%d %H:%M:%S") if snap["created_at"] else "unknown"
        click.echo(f"{snap['label']:<30} {ts:<22} {snap['filename']}")
