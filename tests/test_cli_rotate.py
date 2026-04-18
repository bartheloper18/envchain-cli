"""Tests for CLI rotate and verify commands."""

import pytest
from click.testing import CliRunner
from envchain.vault import create_vault, save_vault
from envchain.cli_rotate import rotate_cmd, verify_cmd


@pytest.fixture
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVCHAIN_DIR", str(tmp_path))
    create_vault("testvault", "oldpass", vault_dir=str(tmp_path))
    save_vault("testvault", {"A": "1"}, "oldpass", vault_dir=str(tmp_path))
    return str(tmp_path)


def test_rotate_cmd_success(vault_dir):
    runner = CliRunner()
    result = runner.invoke(rotate_cmd, ["testvault", "--old-password", "oldpass", "--new-password", "newpass"])
    assert result.exit_code == 0
    assert "rotated successfully" in result.output


def test_rotate_cmd_wrong_old_password(vault_dir):
    runner = CliRunner()
    result = runner.invoke(rotate_cmd, ["testvault", "--old-password", "wrong", "--new-password", "newpass"])
    assert result.exit_code != 0


def test_rotate_cmd_missing_vault(vault_dir):
    runner = CliRunner()
    result = runner.invoke(rotate_cmd, ["ghost", "--old-password", "oldpass", "--new-password", "newpass"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_verify_cmd_correct_password(vault_dir):
    runner = CliRunner()
    result = runner.invoke(verify_cmd, ["testvault", "--password", "oldpass"])
    assert result.exit_code == 0
    assert "correct" in result.output


def test_verify_cmd_wrong_password(vault_dir):
    runner = CliRunner()
    result = runner.invoke(verify_cmd, ["testvault", "--password", "wrongpass"])
    assert result.exit_code != 0
    assert "Incorrect" in result.output
