"""Tests for envchain.snapshot module."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from envchain.snapshot import create_snapshot, restore_snapshot, list_snapshots
from envchain.vault import create_vault, save_vault


@pytest.fixture
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVCHAIN_HOME", str(tmp_path))
    return tmp_path


@pytest.fixture
def populated_vault(vault_dir):
    create_vault("myapp", "secret")
    save_vault("myapp", {"DB_URL": "postgres://localhost", "API_KEY": "abc123"}, "secret")
    return vault_dir


def test_create_snapshot_returns_path(populated_vault):
    path = create_snapshot("snap1", ["myapp"], "secret")
    assert path.exists()
    assert path.suffix == ".snap"


def test_create_snapshot_filename_contains_label(populated_vault):
    path = create_snapshot("mysnap", ["myapp"], "secret")
    assert "mysnap" in path.name


def test_create_snapshot_no_vaults_raises(vault_dir):
    with pytest.raises(ValueError, match="At least one vault"):
        create_snapshot("empty", [], "secret")


def test_create_snapshot_missing_vault_raises(vault_dir):
    with pytest.raises(FileNotFoundError, match="Vault not found"):
        create_snapshot("bad", ["nonexistent"], "secret")


def test_restore_snapshot_recreates_vault(populated_vault):
    snap_path = create_snapshot("restore_test", ["myapp"], "secret")
    # Remove vault to simulate fresh restore
    from envchain.vault import _get_vault_path
    vault_path = _get_vault_path("myapp")
    vault_path.unlink()

    restored = restore_snapshot(snap_path, "secret", overwrite=False)
    assert "myapp" in restored
    assert vault_path.exists()


def test_restore_snapshot_roundtrip_data(populated_vault):
    from envchain.vault import load_vault, _get_vault_path
    snap_path = create_snapshot("roundtrip", ["myapp"], "secret")
    _get_vault_path("myapp").unlink()
    restore_snapshot(snap_path, "secret", overwrite=False)
    data = load_vault("myapp", "secret")
    assert data["DB_URL"] == "postgres://localhost"
    assert data["API_KEY"] == "abc123"


def test_restore_snapshot_no_overwrite_raises(populated_vault):
    snap_path = create_snapshot("no_overwrite", ["myapp"], "secret")
    with pytest.raises(FileExistsError, match="already exists"):
        restore_snapshot(snap_path, "secret", overwrite=False)


def test_restore_snapshot_overwrite_succeeds(populated_vault):
    snap_path = create_snapshot("overwrite_ok", ["myapp"], "secret")
    restored = restore_snapshot(snap_path, "secret", overwrite=True)
    assert "myapp" in restored


def test_restore_missing_file_raises(vault_dir):
    with pytest.raises(FileNotFoundError):
        restore_snapshot(Path(vault_dir / "ghost.snap"), "secret")


def test_list_snapshots_empty(vault_dir):
    result = list_snapshots()
    assert result == []


def test_list_snapshots_returns_entries(populated_vault):
    create_snapshot("alpha", ["myapp"], "secret")
    create_snapshot("beta", ["myapp"], "secret")
    snaps = list_snapshots()
    labels = [s["label"] for s in snaps]
    assert "alpha" in labels
    assert "beta" in labels
