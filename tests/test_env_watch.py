"""Tests for envchain.env_watch."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List
from unittest.mock import call, patch

import pytest

from envchain.env_watch import _diff_snapshots, _hash_vault, poll_vault
from envchain.vault import create_vault, save_vault


# ---------------------------------------------------------------------------
# Unit tests for pure helpers
# ---------------------------------------------------------------------------

def test_hash_vault_is_deterministic():
    data = {"KEY": "value", "OTHER": "stuff"}
    assert _hash_vault(data) == _hash_vault(data)


def test_hash_vault_differs_on_change():
    a = {"KEY": "v1"}
    b = {"KEY": "v2"}
    assert _hash_vault(a) != _hash_vault(b)


def test_diff_snapshots_added():
    diff = _diff_snapshots({}, {"NEW": "1"})
    assert "NEW" in diff["added"]
    assert diff["removed"] == []
    assert diff["changed"] == []


def test_diff_snapshots_removed():
    diff = _diff_snapshots({"OLD": "1"}, {})
    assert "OLD" in diff["removed"]
    assert diff["added"] == []
    assert diff["changed"] == []


def test_diff_snapshots_changed():
    diff = _diff_snapshots({"K": "old"}, {"K": "new"})
    assert "K" in diff["changed"]
    assert diff["added"] == []
    assert diff["removed"] == []


def test_diff_snapshots_no_change():
    diff = _diff_snapshots({"K": "v"}, {"K": "v"})
    assert all(len(v) == 0 for v in diff.values())


# ---------------------------------------------------------------------------
# Integration test for poll_vault
# ---------------------------------------------------------------------------

@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_poll_vault_calls_on_change_when_vars_change(vault_dir: Path):
    password = "secret"
    create_vault("watch_test", password, vault_dir=vault_dir)

    changes: List[Dict] = []

    def _on_change(name: str, diff: Dict) -> None:
        changes.append({"name": name, "diff": diff})

    call_count = 0

    def _fake_load(vault_name, password, vault_dir):
        nonlocal call_count
        call_count += 1
        # First call returns empty; second call returns a new variable.
        if call_count <= 1:
            return {}
        return {"DB_URL": "postgres://localhost"}

    with patch("envchain.env_watch.load_vault", side_effect=_fake_load):
        with patch("envchain.env_watch.time.sleep"):
            poll_vault(
                "watch_test",
                password,
                on_change=_on_change,
                interval=0,
                max_iterations=2,
                vault_dir=vault_dir,
            )

    assert len(changes) == 1
    assert changes[0]["name"] == "watch_test"
    assert "DB_URL" in changes[0]["diff"]["added"]


def test_poll_vault_no_change_no_callback(vault_dir: Path):
    password = "secret"
    create_vault("stable_vault", password, vault_dir=vault_dir)

    called = []

    with patch("envchain.env_watch.load_vault", return_value={"K": "v"}):
        with patch("envchain.env_watch.time.sleep"):
            poll_vault(
                "stable_vault",
                password,
                on_change=lambda n, d: called.append(d),
                interval=0,
                max_iterations=3,
                vault_dir=vault_dir,
            )

    assert called == []
