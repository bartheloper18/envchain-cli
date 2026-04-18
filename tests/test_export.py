"""Tests for envchain.export module."""

import pytest
from pathlib import Path

from envchain.export import export_vault, import_vault, write_export_file, read_export_file


SAMPLE_VAULT = {"API_KEY": "secret123", "DB_URL": "postgres://localhost/db"}
VAULT_NAME = "myproject"
PASSWORD = "correct-horse-battery"


def test_export_returns_bytes():
    bundle = export_vault(SAMPLE_VAULT, PASSWORD, VAULT_NAME)
    assert isinstance(bundle, bytes)
    assert len(bundle) > 0


def test_export_import_roundtrip():
    bundle = export_vault(SAMPLE_VAULT, PASSWORD, VAULT_NAME)
    result = import_vault(bundle, PASSWORD)
    assert result["variables"] == SAMPLE_VAULT
    assert result["vault"] == VAULT_NAME
    assert "exported_at" in result


def test_import_wrong_password_raises():
    bundle = export_vault(SAMPLE_VAULT, PASSWORD, VAULT_NAME)
    with pytest.raises(ValueError, match="Decryption failed"):
        import_vault(bundle, "wrong-password")


def test_import_corrupt_bundle_raises():
    with pytest.raises(ValueError, match="Invalid export bundle"):
        import_vault(b"not-valid-json", PASSWORD)


def test_import_missing_fields_raises():
    import json, base64
    from envchain.crypto import derive_key, generate_salt, encrypt
    salt = generate_salt()
    key = derive_key(PASSWORD, salt)
    # payload missing 'version'
    payload = json.dumps({"vault": "x", "exported_at": "now", "variables": {}}).encode()
    encrypted = encrypt(key, payload)
    bundle = json.dumps({
        "salt": base64.b64encode(salt).decode(),
        "data": base64.b64encode(encrypted).decode(),
    }).encode()
    with pytest.raises(ValueError, match="Unsupported export version"):
        import_vault(bundle, PASSWORD)


def test_export_is_non_deterministic():
    """Each export should produce a different ciphertext due to random salt."""
    bundle1 = export_vault(SAMPLE_VAULT, PASSWORD, VAULT_NAME)
    bundle2 = export_vault(SAMPLE_VAULT, PASSWORD, VAULT_NAME)
    assert bundle1 != bundle2


def test_write_and_read_export_file(tmp_path: Path):
    bundle = export_vault(SAMPLE_VAULT, PASSWORD, VAULT_NAME)
    file_path = tmp_path / "vault.enc"
    write_export_file(file_path, bundle)
    assert file_path.exists()
    loaded = read_export_file(file_path)
    result = import_vault(loaded, PASSWORD)
    assert result["variables"] == SAMPLE_VAULT
