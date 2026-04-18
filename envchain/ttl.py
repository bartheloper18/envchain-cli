"""TTL (time-to-live) management for vault secrets."""
import json
import time
from pathlib import Path
from typing import Optional, Dict

TTL_DIR = Path.home() / ".envchain" / "ttl"


def _get_ttl_path(vault_name: str) -> Path:
    return TTL_DIR / f"{vault_name}.ttl.json"


def set_ttl(vault_name: str, key: str, seconds: int) -> None:
    """Set a TTL for a specific key in a vault."""
    TTL_DIR.mkdir(parents=True, exist_ok=True)
    path = _get_ttl_path(vault_name)
    data = _load_ttl_data(vault_name)
    data[key] = {"expires_at": time.time() + seconds, "ttl": seconds}
    path.write_text(json.dumps(data, indent=2))


def remove_ttl(vault_name: str, key: str) -> None:
    """Remove TTL for a specific key."""
    data = _load_ttl_data(vault_name)
    data.pop(key, None)
    path = _get_ttl_path(vault_name)
    if data:
        path.write_text(json.dumps(data, indent=2))
    elif path.exists():
        path.unlink()


def is_expired(vault_name: str, key: str) -> bool:
    """Return True if the key's TTL has expired."""
    data = _load_ttl_data(vault_name)
    if key not in data:
        return False
    return time.time() > data[key]["expires_at"]


def get_ttl_info(vault_name: str, key: str) -> Optional[Dict]:
    """Return TTL info dict or None if no TTL set."""
    data = _load_ttl_data(vault_name)
    if key not in data:
        return None
    entry = data[key]
    remaining = max(0.0, entry["expires_at"] - time.time())
    return {"ttl": entry["ttl"], "expires_at": entry["expires_at"], "remaining": remaining}


def purge_expired(vault_name: str) -> list:
    """Remove all expired keys and return their names."""
    data = _load_ttl_data(vault_name)
    now = time.time()
    expired = [k for k, v in data.items() if now > v["expires_at"]]
    for k in expired:
        del data[k]
    path = _get_ttl_path(vault_name)
    if data:
        path.write_text(json.dumps(data, indent=2))
    elif path.exists():
        path.unlink()
    return expired


def _load_ttl_data(vault_name: str) -> Dict:
    path = _get_ttl_path(vault_name)
    if not path.exists():
        return {}
    return json.loads(path.read_text())
