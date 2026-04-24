"""Tests for envchain.cli_alias CLI commands."""

import pytest
from click.testing import CliRunner
from envchain.cli_alias import alias_cmd


@pytest.fixture
def runner():
    return CliRunner()


def _invoke(runner, args, base_dir):
    full_args = []
    for arg in args:
        full_args.append(arg)
    # inject --dir before the subcommand's options
    return runner.invoke(alias_cmd, full_args + ["--dir", base_dir])


def test_alias_add_success(runner, tmp_path):
    result = runner.invoke(
        alias_cmd, ["add", "mykey", "myvault", "MY_VAR", "--dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "mykey" in result.output
    assert "myvault:MY_VAR" in result.output


def test_alias_remove_found(runner, tmp_path):
    runner.invoke(
        alias_cmd, ["add", "tok", "vault", "TOKEN", "--dir", str(tmp_path)]
    )
    result = runner.invoke(
        alias_cmd, ["remove", "tok", "--dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "removed" in result.output


def test_alias_remove_not_found(runner, tmp_path):
    result = runner.invoke(
        alias_cmd, ["remove", "ghost", "--dir", str(tmp_path)]
    )
    assert result.exit_code != 0
    assert "not found" in result.output


def test_alias_resolve_success(runner, tmp_path):
    runner.invoke(
        alias_cmd, ["add", "db", "prod", "DB_PASS", "--dir", str(tmp_path)]
    )
    result = runner.invoke(
        alias_cmd, ["resolve", "db", "--dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "prod:DB_PASS" in result.output


def test_alias_resolve_missing(runner, tmp_path):
    result = runner.invoke(
        alias_cmd, ["resolve", "unknown", "--dir", str(tmp_path)]
    )
    assert result.exit_code != 0


def test_alias_list_empty(runner, tmp_path):
    result = runner.invoke(alias_cmd, ["list", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No aliases" in result.output


def test_alias_list_shows_entries(runner, tmp_path):
    runner.invoke(alias_cmd, ["add", "a1", "v1", "K1", "--dir", str(tmp_path)])
    runner.invoke(alias_cmd, ["add", "a2", "v2", "K2", "--dir", str(tmp_path)])
    result = runner.invoke(alias_cmd, ["list", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "a1" in result.output
    assert "v1:K1" in result.output
    assert "a2" in result.output
