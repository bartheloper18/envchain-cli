"""Tests for vault password rotation."""

import pytest
from pathlib import Path
from envchain.vault import create_vault, load_vault
from envchain.rotate import rotate_password, rotate_all, verify_password


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def populated_vault(vault_dir):
    create_vault("myvault", "oldpass", vault_dir=vault_dir)
    from envchain.vault import save_vault
    save_vault("myvault", {"KEY": "value", "FOO": "bar"}, "oldpass", vault_dir=vault_dir)
    return vault_dir


def test_rotate_password_allows_new_password(populated_vault):
    rotate_password("myvault", "oldpass", "newpass", vault_dir=populated_vault)
    data = load_vault("myvault", "newpass", vault_dir=populated_vault)
    assert data["KEY"] == "value"
    assert data["FOO"] == "bar"


def test_rotate_password_old_password_fails_after_rotate(populated_vault):
    rotate_password("myvault", "oldpass", "newpass", vault_dir=populated_vault)
    with pytest.raises(Exception):
        load_vault("myvault", "oldpass", vault_dir=populated_vault)


def test_rotate_wrong_old_password_raises(populated_vault):
    with pytest.raises(Exception):
        rotate_password("myvault", "wrongpass", "newpass", vault_dir=populated_vault)


def test_rotate_nonexistent_vault_raises(vault_dir):
    with pytest.raises(FileNotFoundError):
        rotate_password("ghost", "oldpass", "newpass", vault_dir=vault_dir)


def test_rotate_all_success(vault_dir):
    for name in ["v1", "v2"]:
        create_vault(name, "oldpass", vault_dir=vault_dir)
    results = rotate_all(["v1", "v2"], "oldpass", "newpass", vault_dir=vault_dir)
    assert results["v1"] == "ok"
    assert results["v2"] == "ok"


def test_rotate_all_partial_failure(vault_dir):
    create_vault("good", "oldpass", vault_dir=vault_dir)
    results = rotate_all(["good", "missing"], "oldpass", "newpass", vault_dir=vault_dir)
    assert results["good"] == "ok"
    assert results["missing"].startswith("error:")


def test_verify_password_correct(populated_vault):
    assert verify_password("myvault", "oldpass", vault_dir=populated_vault) is True


def test_verify_password_incorrect(populated_vault):
    assert verify_password("myvault", "wrongpass", vault_dir=populated_vault) is False
