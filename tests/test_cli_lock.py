"""Tests for CLI lock/unlock commands."""

from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envchain.cli_lock import unlock_cmd, lock_cmd, status_cmd


def test_unlock_cmd_output():
    runner = CliRunner()
    with patch("envchain.cli_lock.unlock_vault") as mu, \
         patch("envchain.cli_lock.log_event") as ml:
        result = runner.invoke(unlock_cmd, ["myvault", "--timeout", "120"])
        assert result.exit_code == 0
        assert "myvault" in result.output
        assert "120s" in result.output
        mu.assert_called_once_with("myvault", timeout=120)
        ml.assert_called_once()


def test_lock_cmd_output():
    runner = CliRunner()
    with patch("envchain.cli_lock.lock_vault") as ml, \
         patch("envchain.cli_lock.log_event"):
        result = runner.invoke(lock_cmd, ["myvault"])
        assert result.exit_code == 0
        assert "locked" in result.output
        ml.assert_called_once_with("myvault")


def test_status_cmd_unlocked():
    runner = CliRunner()
    fake_info = {"vault": "myvault", "unlocked_at": 0.0, "expires_at": 9999999999.0}
    with patch("envchain.cli_lock.get_lock_info", return_value=fake_info):
        result = runner.invoke(status_cmd, ["myvault"])
        assert result.exit_code == 0
        assert "unlocked" in result.output


def test_status_cmd_locked():
    runner = CliRunner()
    with patch("envchain.cli_lock.get_lock_info", return_value=None), \
         patch("envchain.cli_lock.is_unlocked", return_value=False):
        result = runner.invoke(status_cmd, ["myvault"])
        assert result.exit_code == 0
        assert "locked" in result.output
