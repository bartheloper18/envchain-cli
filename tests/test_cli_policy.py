"""Tests for envchain.cli_policy module."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envchain.cli_policy import policy_cmd


@pytest.fixture
def runner():
    return CliRunner()


def test_policy_add_success(runner):
    with patch("envchain.cli_policy.add_rule") as mock_add:
        result = runner.invoke(policy_cmd, ["add", "myvault", "read", "SECRET_*", "--effect", "deny"])
        assert result.exit_code == 0
        assert "Rule added" in result.output
        mock_add.assert_called_once_with("myvault", "read", "SECRET_*", "deny")


def test_policy_remove_found(runner):
    with patch("envchain.cli_policy.remove_rule", return_value=True):
        result = runner.invoke(policy_cmd, ["remove", "myvault", "read", "SECRET_*"])
        assert result.exit_code == 0
        assert "Rule removed" in result.output


def test_policy_remove_not_found(runner):
    with patch("envchain.cli_policy.remove_rule", return_value=False):
        result = runner.invoke(policy_cmd, ["remove", "myvault", "read", "GHOST"])
        assert "No matching rule found" in result.output


def test_policy_list_no_rules(runner):
    with patch("envchain.cli_policy.load_policy", return_value={"default": "allow", "rules": []}):
        result = runner.invoke(policy_cmd, ["list", "myvault"])
        assert result.exit_code == 0
        assert "No rules defined" in result.output
        assert "Default: allow" in result.output


def test_policy_list_with_rules(runner):
    policy = {"default": "deny", "rules": [{"action": "read", "key_pattern": "DB_*", "effect": "allow"}]}
    with patch("envchain.cli_policy.load_policy", return_value=policy):
        result = runner.invoke(policy_cmd, ["list", "myvault"])
        assert "[ALLOW] read on 'DB_*'" in result.output
        assert "Default: deny" in result.output


def test_policy_check_allowed(runner):
    with patch("envchain.cli_policy.is_allowed", return_value=True):
        result = runner.invoke(policy_cmd, ["check", "myvault", "read", "MY_KEY"])
        assert "ALLOWED" in result.output


def test_policy_check_denied(runner):
    with patch("envchain.cli_policy.is_allowed", return_value=False):
        result = runner.invoke(policy_cmd, ["check", "myvault", "delete", "SECRET_KEY"])
        assert "DENIED" in result.output


def test_policy_default_set(runner):
    with patch("envchain.cli_policy.set_default") as mock_set:
        result = runner.invoke(policy_cmd, ["default", "myvault", "deny"])
        assert result.exit_code == 0
        assert "deny" in result.output
        mock_set.assert_called_once_with("myvault", "deny")
