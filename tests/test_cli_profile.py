"""Tests for envchain.cli_profile CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch
from envchain.cli_profile import profile_cmd
from envchain import profile as profile_mod


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def profile_dir(tmp_path):
    return tmp_path / "profiles"


def _patch(profile_dir):
    return patch.multiple(
        profile_mod,
        DEFAULT_PROFILES_DIR=profile_dir,
    )


def test_profile_create(runner, profile_dir):
    with patch("envchain.cli_profile.create_profile", wraps=lambda n, v, profiles_dir=None: profile_mod.create_profile(n, v, profiles_dir=profile_dir)) as mock:
        result = runner.invoke(profile_cmd, ["create", "dev", "app", "db"])
    assert result.exit_code == 0
    assert "created" in result.output


def test_profile_create_duplicate(runner, profile_dir):
    profile_mod.create_profile("dev", [], profiles_dir=profile_dir)
    with patch("envchain.cli_profile.create_profile", side_effect=FileExistsError("Profile 'dev' already exists.")):
        result = runner.invoke(profile_cmd, ["create", "dev"])
    assert result.exit_code == 1


def test_profile_list_empty(runner, profile_dir):
    with patch("envchain.cli_profile.list_profiles", return_value=[]):
        result = runner.invoke(profile_cmd, ["list"])
    assert "No profiles" in result.output


def test_profile_list_names(runner, profile_dir):
    with patch("envchain.cli_profile.list_profiles", return_value=["dev", "prod"]):
        result = runner.invoke(profile_cmd, ["list"])
    assert "dev" in result.output
    assert "prod" in result.output


def test_profile_show(runner, profile_dir):
    with patch("envchain.cli_profile.load_profile", return_value={"name": "dev", "vaults": ["app", "db"]}):
        result = runner.invoke(profile_cmd, ["show", "dev"])
    assert "app" in result.output
    assert "db" in result.output


def test_profile_delete(runner):
    with patch("envchain.cli_profile.delete_profile", return_value=True):
        result = runner.invoke(profile_cmd, ["delete", "dev"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_profile_add_vault(runner):
    with patch("envchain.cli_profile.add_vault_to_profile") as mock:
        result = runner.invoke(profile_cmd, ["add-vault", "dev", "secrets"])
    assert result.exit_code == 0
    assert "added" in result.output


def test_profile_remove_vault(runner):
    with patch("envchain.cli_profile.remove_vault_from_profile", return_value=True):
        result = runner.invoke(profile_cmd, ["remove-vault", "dev", "secrets"])
    assert result.exit_code == 0
    assert "removed" in result.output
