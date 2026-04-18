"""Tests for the vault module."""

import pytest
from unittest.mock import patch
from pathlib import Path
import tempfile

import envchain.vault as vault_module
from envchain.vault import create_vault, load_vault, save_vault, list_vaults


@pytest.fixture(autouse=True)
def temp_vault_dir(tmp_path):
    """Redirect vault storage to a temporary directory for each test."""
    with patch.object(vault_module, "DEFAULT_VAULT_DIR", tmp_path / "vaults"):
        yield


def test_create_vault_creates_files():
    path = create_vault("myapp")
    assert path.exists()


def test_create_vault_duplicate_raises():
    create_vault("myapp")
    with pytest.raises(FileExistsError):
        create_vault("myapp")


def test_load_empty_vault():
    create_vault("myapp")
    data = load_vault("myapp")
    assert data == {}


def test_save_and_load_vault():
    create_vault("myapp")
    save_vault("myapp", {"API_KEY": "secret123", "DEBUG": "true"})
    data = load_vault("myapp")
    assert data["API_KEY"] == "secret123"
    assert data["DEBUG"] == "true"


def test_load_nonexistent_vault_raises():
    with pytest.raises(FileNotFoundError):
        load_vault("ghost")


def test_list_vaults_empty():
    assert list_vaults() == []


def test_list_vaults_returns_names():
    create_vault("alpha")
    create_vault("beta")
    vaults = list_vaults()
    assert set(vaults) == {"alpha", "beta"}
