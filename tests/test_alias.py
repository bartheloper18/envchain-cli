"""Tests for envchain.alias module."""

import pytest
from pathlib import Path
from envchain.alias import (
    add_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    load_aliases,
)


@pytest.fixture
def alias_dir(tmp_path):
    return str(tmp_path)


def test_load_aliases_empty(alias_dir):
    assert load_aliases(alias_dir) == {}


def test_add_alias_creates_entry(alias_dir):
    add_alias(alias_dir, "db_pass", "myapp", "DB_PASSWORD")
    aliases = load_aliases(alias_dir)
    assert "db_pass" in aliases
    assert aliases["db_pass"] == {"vault": "myapp", "key": "DB_PASSWORD"}


def test_add_alias_overwrites_existing(alias_dir):
    add_alias(alias_dir, "token", "vault1", "API_TOKEN")
    add_alias(alias_dir, "token", "vault2", "NEW_TOKEN")
    result = resolve_alias(alias_dir, "token")
    assert result == {"vault": "vault2", "key": "NEW_TOKEN"}


def test_add_alias_invalid_raises(alias_dir):
    with pytest.raises(ValueError):
        add_alias(alias_dir, "", "vault", "KEY")
    with pytest.raises(ValueError):
        add_alias(alias_dir, "name", "", "KEY")
    with pytest.raises(ValueError):
        add_alias(alias_dir, "name", "vault", "")


def test_resolve_alias_returns_target(alias_dir):
    add_alias(alias_dir, "secret", "prod", "SECRET_KEY")
    result = resolve_alias(alias_dir, "secret")
    assert result == {"vault": "prod", "key": "SECRET_KEY"}


def test_resolve_alias_missing_returns_none(alias_dir):
    assert resolve_alias(alias_dir, "nonexistent") is None


def test_remove_alias_returns_true(alias_dir):
    add_alias(alias_dir, "myalias", "v", "K")
    assert remove_alias(alias_dir, "myalias") is True
    assert resolve_alias(alias_dir, "myalias") is None


def test_remove_alias_missing_returns_false(alias_dir):
    assert remove_alias(alias_dir, "ghost") is False


def test_list_aliases_sorted(alias_dir):
    add_alias(alias_dir, "zebra", "v", "Z")
    add_alias(alias_dir, "alpha", "v", "A")
    add_alias(alias_dir, "mango", "v", "M")
    entries = list_aliases(alias_dir)
    names = [e["alias"] for e in entries]
    assert names == sorted(names)


def test_list_aliases_empty(alias_dir):
    assert list_aliases(alias_dir) == []
