"""Tests for envchain.lock module."""

import time
import pytest
from pathlib import Path
from envchain.lock import lock_vault, unlock_vault, is_unlocked, get_lock_info


@pytest.fixture
def lock_dir(tmp_path):
    return str(tmp_path)


def test_unlock_creates_lock_file(lock_dir):
    unlock_vault("myvault", timeout=60, base_dir=lock_dir)
    lock_file = Path(lock_dir) / "myvault.lock"
    assert lock_file.exists()


def test_is_unlocked_after_unlock(lock_dir):
    unlock_vault("myvault", timeout=60, base_dir=lock_dir)
    assert is_unlocked("myvault", base_dir=lock_dir) is True


def test_is_locked_before_unlock(lock_dir):
    assert is_unlocked("myvault", base_dir=lock_dir) is False


def test_lock_vault_removes_lock_file(lock_dir):
    unlock_vault("myvault", timeout=60, base_dir=lock_dir)
    lock_vault("myvault", base_dir=lock_dir)
    assert is_unlocked("myvault", base_dir=lock_dir) is False


def test_expired_lock_returns_false(lock_dir):
    unlock_vault("myvault", timeout=0, base_dir=lock_dir)
    time.sleep(0.05)
    assert is_unlocked("myvault", base_dir=lock_dir) is False


def test_get_lock_info_returns_metadata(lock_dir):
    unlock_vault("myvault", timeout=60, base_dir=lock_dir)
    info = get_lock_info("myvault", base_dir=lock_dir)
    assert info is not None
    assert info["vault"] == "myvault"
    assert "unlocked_at" in info
    assert "expires_at" in info


def test_get_lock_info_returns_none_when_locked(lock_dir):
    assert get_lock_info("myvault", base_dir=lock_dir) is None


def test_lock_vault_noop_when_already_locked(lock_dir):
    lock_vault("myvault", base_dir=lock_dir)  # should not raise
    assert is_unlocked("myvault", base_dir=lock_dir) is False
