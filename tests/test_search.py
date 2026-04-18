"""Tests for envchain.search module."""

from __future__ import annotations

import pytest

from envchain.search import format_results, search_all_vaults, search_vars
from envchain.vault import create_vault, save_vault


@pytest.fixture()
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVCHAIN_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture()
def populated_vault(vault_dir):
    create_vault("myvault", "secret")
    save_vault("myvault", "secret", {"DATABASE_URL": "postgres://localhost", "API_KEY": "abc123", "DEBUG": "true"})
    return "myvault"


def test_search_by_key(populated_vault):
    results = search_vars("myvault", "secret", "API")
    assert len(results) == 1
    assert results[0]["key"] == "API_KEY"


def test_search_by_value(populated_vault):
    results = search_vars("myvault", "secret", "postgres")
    assert len(results) == 1
    assert results[0]["key"] == "DATABASE_URL"


def test_search_case_insensitive(populated_vault):
    results = search_vars("myvault", "secret", "database")
    assert len(results) == 1


def test_search_keys_only_skips_value_match(populated_vault):
    results = search_vars("myvault", "secret", "postgres", keys_only=True)
    assert len(results) == 0


def test_search_keys_only_no_value_in_result(populated_vault):
    results = search_vars("myvault", "secret", "DEBUG", keys_only=True)
    assert len(results) == 1
    assert "value" not in results[0]


def test_search_no_match(populated_vault):
    results = search_vars("myvault", "secret", "NONEXISTENT")
    assert results == []


def test_search_all_vaults_skips_bad_password(vault_dir):
    create_vault("v1", "pass1")
    save_vault("v1", "pass1", {"FOO": "bar"})
    create_vault("v2", "pass2")
    save_vault("v2", "pass2", {"FOO": "baz"})
    results = search_all_vaults(["v1", "v2"], "pass1", "FOO")
    assert len(results) == 1
    assert results[0]["vault"] == "v1"


def test_format_results_with_values():
    results = [{"vault": "v1", "key": "FOO", "value": "baresults(results)
    assert "[v1] FOO = bar" in output


def test_format_results_no_match():
    assert format_results([]) == "No matches found."
