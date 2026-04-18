"""Backup and restore vaults to/from a directory."""

import os
import shutil
from datetime import datetime
from pathlib import Path

from envchain.vault import _get_vault_path, _get_key_path


def _backup_dir() -> Path:
    base = Path(os.environ.get("ENVCHAIN_HOME", Path.home() / ".envchain"))
    return base / "backups"


def backup_vault(vault_name: str, dest_dir: Path | None = None) -> Path:
    """Copy vault + key files into a timestamped backup folder."""
    vault_path = _get_vault_path(vault_name)
    key_path = _get_key_path(vault_name)

    if not vault_path.exists():
        raise FileNotFoundError(f"Vault '{vault_name}' does not exist.")

    dest_dir = dest_dir or _backup_dir()
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup_path = dest_dir / f"{vault_name}_{timestamp}"
    backup_path.mkdir(parents=True, exist_ok=True)

    shutil.copy2(vault_path, backup_path / vault_path.name)
    shutil.copy2(key_path, backup_path / key_path.name)

    return backup_path


def restore_vault(backup_path: Path, overwrite: bool = False) -> str:
    """Restore a vault from a backup folder. Returns vault name."""
    vault_files = list(backup_path.glob("*.vault"))
    key_files = list(backup_path.glob("*.key"))

    if not vault_files or not key_files:
        raise ValueError(f"Backup at '{backup_path}' is missing vault or key file.")

    vault_file = vault_files[0]
    key_file = key_files[0]
    vault_name = vault_file.stem

    dest_vault = _get_vault_path(vault_name)
    dest_key = _get_key_path(vault_name)

    if dest_vault.exists() and not overwrite:
        raise FileExistsError(
            f"Vault '{vault_name}' already exists. Use overwrite=True to replace."
        )

    dest_vault.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(vault_file, dest_vault)
    shutil.copy2(key_file, dest_key)

    return vault_name


def list_backups(vault_name: str | None = None, dest_dir: Path | None = None) -> list[Path]:
    """List available backups, optionally filtered by vault name."""
    dest_dir = dest_dir or _backup_dir()
    if not dest_dir.exists():
        return []
    entries = sorted(dest_dir.iterdir())
    if vault_name:
        entries = [e for e in entries if e.name.startswith(f"{vault_name}_")]
    return [e for e in entries if e.is_dir()]
