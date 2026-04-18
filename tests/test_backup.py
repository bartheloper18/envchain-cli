"""Tests for envchain.backup module."""

import pytest
from pathlib import Path

from envchain.vault import create_vault
from envchain.backup import backup_vault, restore_vault, list_backups


@pytest.fixture
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVCHAIN_HOME", str(tmp_path))
    return tmp_path


def test_backup_creates_snapshot(vault_dir):
    create_vault("myapp", "secret")
    backup_path = backup_vault("myapp", dest_dir=vault_dir / "backups")
    assert backup_path.exists()
    assert any(f.suffix == ".vault" for f in backup_path.iterdir())
    assert any(f.suffix == ".key" for f in backup_path.iterdir())


def test_backup_nonexistent_vault_raises(vault_dir):
    with pytest.raises(FileNotFoundError):
        backup_vault("ghost", dest_dir=vault_dir / "backups")


def test_restore_vault(vault_dir):
    create_vault("alpha", "pass1")
    backup_path = backup_vault("alpha", dest_dir=vault_dir / "backups")

    # Remove original
    (vault_dir / "vaults" / "alpha.vault").unlink()
    (vault_dir / "vaults" / "alpha.key").unlink()

    name = restore_vault(backup_path)
    assert name == "alpha"
    assert (vault_dir / "vaults" / "alpha.vault").exists()


def test_restore_no_overwrite_raises(vault_dir):
    create_vault("beta", "pass")
    backup_path = backup_vault("beta", dest_dir=vault_dir / "backups")
    with pytest.raises(FileExistsError):
        restore_vault(backup_path, overwrite=False)


def test_restore_with_overwrite(vault_dir):
    create_vault("gamma", "pass")
    backup_path = backup_vault("gamma", dest_dir=vault_dir / "backups")
    name = restore_vault(backup_path, overwrite=True)
    assert name == "gamma"


def test_list_backups_empty(vault_dir):
    result = list_backups(dest_dir=vault_dir / "backups")
    assert result == []


def test_list_backups_filtered(vault_dir):
    create_vault("v1", "p")
    create_vault("v2", "p")
    backup_vault("v1", dest_dir=vault_dir / "backups")
    backup_vault("v2", dest_dir=vault_dir / "backups")
    results = list_backups("v1", dest_dir=vault_dir / "backups")
    assert all("v1" in str(r) for r in results)
    assert len(results) == 1
