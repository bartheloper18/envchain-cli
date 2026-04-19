"""Tests for envchain.profile module."""

import pytest
from pathlib import Path
from envchain.profile import (
    create_profile, load_profile, save_profile, delete_profile,
    list_profiles, add_vault_to_profile, remove_vault_from_profile,
)


@pytest.fixture
def profile_dir(tmp_path):
    return tmp_path / "profiles"


def test_create_profile_creates_file(profile_dir):
    path = create_profile("dev", ["app", "db"], profiles_dir=profile_dir)
    assert path.exists()


def test_create_profile_stores_vaults(profile_dir):
    create_profile("dev", ["app", "db"], profiles_dir=profile_dir)
    data = load_profile("dev", profiles_dir=profile_dir)
    assert data["vaults"] == ["app", "db"]
    assert data["name"] == "dev"


def test_create_profile_duplicate_raises(profile_dir):
    create_profile("dev", [], profiles_dir=profile_dir)
    with pytest.raises(FileExistsError):
        create_profile("dev", [], profiles_dir=profile_dir)


def test_load_profile_not_found_raises(profile_dir):
    with pytest.raises(FileNotFoundError):
        load_profile("missing", profiles_dir=profile_dir)


def test_delete_profile_returns_true(profile_dir):
    create_profile("dev", [], profiles_dir=profile_dir)
    assert delete_profile("dev", profiles_dir=profile_dir) is True


def test_delete_profile_missing_returns_false(profile_dir):
    assert delete_profile("ghost", profiles_dir=profile_dir) is False


def test_list_profiles_empty(profile_dir):
    assert list_profiles(profiles_dir=profile_dir) == []


def test_list_profiles_returns_names(profile_dir):
    create_profile("alpha", [], profiles_dir=profile_dir)
    create_profile("beta", [], profiles_dir=profile_dir)
    names = list_profiles(profiles_dir=profile_dir)
    assert "alpha" in names
    assert "beta" in names


def test_add_vault_to_profile(profile_dir):
    create_profile("dev", [], profiles_dir=profile_dir)
    add_vault_to_profile("dev", "secrets", profiles_dir=profile_dir)
    data = load_profile("dev", profiles_dir=profile_dir)
    assert "secrets" in data["vaults"]


def test_add_vault_no_duplicates(profile_dir):
    create_profile("dev", ["secrets"], profiles_dir=profile_dir)
    add_vault_to_profile("dev", "secrets", profiles_dir=profile_dir)
    data = load_profile("dev", profiles_dir=profile_dir)
    assert data["vaults"].count("secrets") == 1


def test_remove_vault_from_profile(profile_dir):
    create_profile("dev", ["app", "db"], profiles_dir=profile_dir)
    result = remove_vault_from_profile("dev", "app", profiles_dir=profile_dir)
    assert result is True
    data = load_profile("dev", profiles_dir=profile_dir)
    assert "app" not in data["vaults"]


def test_remove_vault_not_present_returns_false(profile_dir):
    create_profile("dev", [], profiles_dir=profile_dir)
    assert remove_vault_from_profile("dev", "missing", profiles_dir=profile_dir) is False
