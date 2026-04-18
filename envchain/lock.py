"""Vault locking and session timeout management."""

import json
import os
import time
from pathlib import Path

DEFAULT_TIMEOUT = 300  # seconds


def _get_lock_path(vault_name: str, base_dir: str | None = None) -> Path:
    base = Path(base_dir) if base_dir else Path.home() / ".envchain"
    return base / f"{vault_name}.lock"


def lock_vault(vault_name: str, base_dir: str | None = None) -> None:
    """Remove the lock file, effectively locking the vault."""
    lock_path = _get_lock_path(vault_name, base_dir)
    if lock_path.exists():
        lock_path.unlink()


def unlock_vault(vault_name: str, timeout: int = DEFAULT_TIMEOUT, base_dir: str | None = None) -> None:
    """Create a lock file with expiry timestamp to mark vault as unlocked."""
    lock_path = _get_lock_path(vault_name, base_dir)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "vault": vault_name,
        "unlocked_at": time.time(),
        "expires_at": time.time() + timeout,
    }
    lock_path.write_text(json.dumps(data))


def is_unlocked(vault_name: str, base_dir: str | None = None) -> bool:
    """Return True if the vault is currently unlocked and session has not expired."""
    lock_path = _get_lock_path(vault_name, base_dir)
    if not lock_path.exists():
        return False
    try:
        data = json.loads(lock_path.read_text())
        return time.time() < data["expires_at"]
    except (json.JSONDecodeError, KeyError):
        return False


def get_lock_info(vault_name: str, base_dir: str | None = None) -> dict | None:
    """Return lock metadata or None if vault is locked/expired."""
    if not is_unlocked(vault_name, base_dir):
        return None
    lock_path = _get_lock_path(vault_name, base_dir)
    try:
        return json.loads(lock_path.read_text())
    except (json.JSONDecodeError, KeyError):
        return None
