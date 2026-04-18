"""Core vault module for managing encrypted environment variable storage."""

import json
import os
from pathlib import Path
from cryptography.fernet import Fernet


DEFAULT_VAULT_DIR = Path.home() / ".envchain" / "vaults"


def _get_vault_path(vault_name: str) -> Path:
    return DEFAULT_VAULT_DIR / f"{vault_name}.vault"


def _get_key_path(vault_name: str) -> Path:
    return DEFAULT_VAULT_DIR / f"{vault_name}.key"


def create_vault(vault_name: str) -> Path:
    """Create a new empty encrypted vault."""
    DEFAULT_VAULT_DIR.mkdir(parents=True, exist_ok=True)
    vault_path = _get_vault_path(vault_name)
    key_path = _get_key_path(vault_name)

    if vault_path.exists():
        raise FileExistsError(f"Vault '{vault_name}' already exists.")

    key = Fernet.generate_key()
    key_path.write_bytes(key)
    key_path.chmod(0o600)

    fernet = Fernet(key)
    encrypted = fernet.encrypt(json.dumps({}).encode())
    vault_path.write_bytes(encrypted)
    vault_path.chmod(0o600)

    return vault_path


def load_vault(vault_name: str) -> dict:
    """Load and decrypt a vault, returning its key-value pairs."""
    vault_path = _get_vault_path(vault_name)
    key_path = _get_key_path(vault_name)

    if not vault_path.exists():
        raise FileNotFoundError(f"Vault '{vault_name}' does not exist.")

    key = key_path.read_bytes()
    fernet = Fernet(key)
    decrypted = fernet.decrypt(vault_path.read_bytes())
    return json.loads(decrypted.decode())


def save_vault(vault_name: str, data: dict) -> None:
    """Encrypt and save data to a vault."""
    key_path = _get_key_path(vault_name)
    vault_path = _get_vault_path(vault_name)

    if not key_path.exists():
        raise FileNotFoundError(f"Key for vault '{vault_name}' not found.")

    key = key_path.read_bytes()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(json.dumps(data).encode())
    vault_path.write_bytes(encrypted)


def list_vaults() -> list:
    """Return a list of available vault names."""
    if not DEFAULT_VAULT_DIR.exists():
        return []
    return [p.stem for p in DEFAULT_VAULT_DIR.glob("*.vault")]
