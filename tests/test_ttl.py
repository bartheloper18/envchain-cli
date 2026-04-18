"""Tests for envchain.ttl module."""
import time
import pytest
from pathlib import Path
from unittest.mock import patch
from envchain.ttl import set_ttl, remove_ttl, is_expired, get_ttl_info, purge_expired


@pytest.fixture(autouse=True)
def ttl_dir(tmp_path, monkeypatch):
    ttl_path = tmp_path / "ttl"
    monkeypatch.setattr("envchain.ttl.TTL_DIR", ttl_path)
    return ttl_path


def test_set_ttl_creates_file(ttl_dir):
    set_ttl("myvault", "API_KEY", 300)
    assert (ttl_dir / "myvault.ttl.json").exists()


def test_get_ttl_info_returns_correct_fields():
    set_ttl("myvault", "API_KEY", 300)
    info = get_ttl_info("myvault", "API_KEY")
    assert info is not None
    assert info["ttl"] == 300
    assert info["remaining"] > 0
    assert "expires_at" in info


def test_get_ttl_info_missing_key_returns_none():
    assert get_ttl_info("myvault", "MISSING") is None


def test_is_not_expired_for_future_ttl():
    set_ttl("myvault", "TOKEN", 600)
    assert not is_expired("myvault", "TOKEN")


def test_is_expired_for_past_ttl():
    set_ttl("myvault", "TOKEN", 1)
    with patch("envchain.ttl.time") as mock_time:
        mock_time.time.return_value = time.time() + 10
        assert is_expired("myvault", "TOKEN")


def test_remove_ttl_cleans_entry():
    set_ttl("myvault", "API_KEY", 300)
    remove_ttl("myvault", "API_KEY")
    assert get_ttl_info("myvault", "API_KEY") is None


def test_remove_ttl_deletes_file_when_empty(ttl_dir):
    set_ttl("myvault", "ONLY_KEY", 300)
    remove_ttl("myvault", "ONLY_KEY")
    assert not (ttl_dir / "myvault.ttl.json").exists()


def test_purge_expired_removes_old_keys():
    set_ttl("myvault", "OLD", 1)
    set_ttl("myvault", "NEW", 600)
    with patch("envchain.ttl.time") as mock_time:
        mock_time.time.return_value = time.time() + 10
        removed = purge_expired("myvault")
    assert "OLD" in removed
    assert "NEW" not in removed


def test_purge_expired_no_expired_returns_empty():
    set_ttl("myvault", "ALIVE", 600)
    removed = purge_expired("myvault")
    assert removed == []
