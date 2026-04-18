"""Password rotation for encrypted vaults."""

from pathlib import Path
from envchain.vault import load_vault, save_vault, _get_key_path
from envchain.crypto import generate_salt, derive_key, encrypt, decrypt
import json
import base64


def rotate_password(vault_name: str, old_password: str, new_password: str, vault_dir: str = None) -> None:
    """Re-encrypt a vault with a new password."""
    # Load vault data with old password
    variables = load_vault(vault_name, old_password, vault_dir=vault_dir)

    # Save vault with new password
    save_vault(vault_name, variables, new_password, vault_dir=vault_dir)


def rotate_all(vault_names: list, old_password: str, new_password: str, vault_dir: str = None) -> dict:
    """Rotate password for multiple vaults. Returns dict of vault -> success/error."""
    results = {}
    for name in vault_names:
        try:
            rotate_password(name, old_password, new_password, vault_dir=vault_dir)
            results[name] = "ok"
        except Exception as e:
            results[name] = f"error: {e}"
    return results


def verify_password(vault_name: str, password: str, vault_dir: str = None) -> bool:
    """Return True if the given password can decrypt the vault."""
    try:
        load_vault(vault_name, password, vault_dir=vault_dir)
        return True
    except Exception:
        return False
