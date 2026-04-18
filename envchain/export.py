"""Export and import vault contents to/from portable encrypted files."""

import json
import base64
import os
from pathlib import Path
from datetime import datetime, timezone

from envchain.crypto import derive_key, generate_salt, encrypt, decrypt


EXPORT_VERSION = 1


def export_vault(vault_data: dict, password: str, vault_name: str) -> bytes:
    """Serialize and encrypt vault data for export."""
    salt = generate_salt()
    key = derive_key(password, salt)

    payload = json.dumps({
        "version": EXPORT_VERSION,
        "vault": vault_name,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "variables": vault_data,
    }).encode()

    encrypted = encrypt(key, payload)

    bundle = json.dumps({
        "salt": base64.b64encode(salt).decode(),
        "data": base64.b64encode(encrypted).decode(),
    })
    return bundle.encode()


def import_vault(bundle_bytes: bytes, password: str) -> dict:
    """Decrypt and deserialize an exported vault bundle.

    Returns a dict with keys: vault, exported_at, variables.
    Raises ValueError on bad password or corrupt data.
    """
    try:
        bundle = json.loads(bundle_bytes)
        salt = base64.b64decode(bundle["salt"])
        encrypted = base64.b64decode(bundle["data"])
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid export bundle: {exc}") from exc

    key = derive_key(password, salt)
    try:
        plaintext = decrypt(key, encrypted)
    except Exception as exc:
        raise ValueError("Decryption failed — wrong password or corrupt file.") from exc

    payload = json.loads(plaintext)
    if payload.get("version") != EXPORT_VERSION:
        raise ValueError(f"Unsupported export version: {payload.get('version')}")

    return {
        "vault": payload["vault"],
        "exported_at": payload["exported_at"],
        "variables": payload["variables"],
    }


def write_export_file(path: str | Path, bundle: bytes) -> None:
    """Write an export bundle to a file."""
    Path(path).write_bytes(bundle)


def read_export_file(path: str | Path) -> bytes:
    """Read an export bundle from a file."""
    return Path(path).read_bytes()
