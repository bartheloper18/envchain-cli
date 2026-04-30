"""Watch vault variables for changes and emit events."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional

from envchain.vault import load_vault


def _hash_vault(variables: Dict[str, str]) -> str:
    """Return a stable hash of the vault variable dict."""
    serialised = json.dumps(variables, sort_keys=True).encode()
    return hashlib.sha256(serialised).hexdigest()


def _diff_snapshots(
    old: Dict[str, str], new: Dict[str, str]
) -> Dict[str, List[str]]:
    """Return a dict describing what changed between two snapshots."""
    added = [k for k in new if k not in old]
    removed = [k for k in old if k not in new]
    changed = [k for k in new if k in old and old[k] != new[k]]
    return {"added": added, "removed": removed, "changed": changed}


def poll_vault(
    vault_name: str,
    password: str,
    on_change: Callable[[str, Dict[str, List[str]]], None],
    interval: float = 2.0,
    max_iterations: Optional[int] = None,
    vault_dir: Optional[Path] = None,
) -> None:
    """Poll a vault at *interval* seconds and call *on_change* when variables change.

    Args:
        vault_name: Name of the vault to watch.
        password: Decryption password.
        on_change: Callback receiving (vault_name, diff_dict).
        interval: Polling interval in seconds.
        max_iterations: Stop after this many iterations (``None`` = run forever).
        vault_dir: Override default vault directory (useful for tests).
    """
    kwargs: Dict = {"password": password}
    if vault_dir is not None:
        kwargs["vault_dir"] = vault_dir

    current = load_vault(vault_name, **kwargs)
    last_hash = _hash_vault(current)
    iterations = 0

    while max_iterations is None or iterations < max_iterations:
        time.sleep(interval)
        updated = load_vault(vault_name, **kwargs)
        new_hash = _hash_vault(updated)
        if new_hash != last_hash:
            diff = _diff_snapshots(current, updated)
            on_change(vault_name, diff)
            current = updated
            last_hash = new_hash
        iterations += 1
