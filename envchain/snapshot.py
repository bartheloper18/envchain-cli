"""Snapshot management: create and restore point-in-time snapshots of all vaults."""

import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any

from envchain.vault import _get_vault_path, load_vault, save_vault


def _get_snapshot_dir() -> Path:
    base = Path(os.environ.get("ENVCHAIN_HOME", Path.home() / ".envchain"))
    d = base / "snapshots"
    d.mkdir(parents=True, exist_ok=True)
    return d


def create_snapshot(label: str, vault_names: List[str], password: str) -> Path:
    """Create a snapshot of the given vaults, encrypted with password."""
    from envchain.crypto import encrypt, generate_salt, derive_key

    if not vault_names:
        raise ValueError("At least one vault name is required.")

    data: Dict[str, Any] = {"label": label, "created_at": time.time(), "vaults": {}}

    for name in vault_names:
        vault_path = _get_vault_path(name)
        if not vault_path.exists():
            raise FileNotFoundError(f"Vault not found: {name}")
        data["vaults"][name] = load_vault(name, password)

    salt = generate_salt()
    key = derive_key(password, salt)
    plaintext = json.dumps(data).encode()
    ciphertext = encrypt(plaintext, key)

    snapshot_dir = _get_snapshot_dir()
    filename = f"{label}_{int(data['created_at'])}.snap"
    snap_path = snapshot_dir / filename

    with open(snap_path, "wb") as f:
        f.write(salt + ciphertext)

    return snap_path


def restore_snapshot(snap_path: Path, password: str, overwrite: bool = False) -> List[str]:
    """Restore vaults from a snapshot file. Returns list of restored vault names."""
    from envchain.crypto import decrypt, derive_key

    if not snap_path.exists():
        raise FileNotFoundError(f"Snapshot not found: {snap_path}")

    with open(snap_path, "rb") as f:
        raw = f.read()

    salt = raw[:16]
    ciphertext = raw[16:]
    key = derive_key(password, salt)
    plaintext = decrypt(ciphertext, key)
    data = json.loads(plaintext.decode())

    restored = []
    for name, variables in data["vaults"].items():
        vault_path = _get_vault_path(name)
        if vault_path.exists() and not overwrite:
            raise FileExistsError(f"Vault already exists: {name}. Use overwrite=True to replace.")
        save_vault(name, variables, password)
        restored.append(name)

    return restored


def list_snapshots() -> List[Dict[str, Any]]:
    """Return metadata for all available snapshots."""
    snap_dir = _get_snapshot_dir()
    results = []
    for f in sorted(snap_dir.glob("*.snap")):
        parts = f.stem.rsplit("_", 1)
        label = parts[0] if len(parts) == 2 else f.stem
        created_at = int(parts[1]) if len(parts) == 2 and parts[1].isdigit() else 0
        results.append({"label": label, "created_at": created_at, "path": str(f), "filename": f.name})
    return results
