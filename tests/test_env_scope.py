"""Tests for envchain.env_scope module."""

import json
import pytest
from pathlib import Path

from envchain.env_scope import (
    load_scope,
    save_scope,
    add_allow,
    add_deny,
    remove_rule,
    apply_scope,
)


@pytest.fixture
def scope_dir(tmp_path: Path) -> str:
    vault = tmp_path / "myvault"
    vault.mkdir()
    return str(tmp_path)


def test_load_scope_default_when_missing(scope_dir):
    scope = load_scope(scope_dir, "myvault")
    assert scope == {"allow": [], "deny": []}


def test_save_and_load_scope(scope_dir):
    save_scope(scope_dir, "myvault", {"allow": ["FOO"], "deny": ["BAR"]})
    scope = load_scope(scope_dir, "myvault")
    assert scope["allow"] == ["FOO"]
    assert scope["deny"] == ["BAR"]


def test_add_allow_adds_key(scope_dir):
    add_allow(scope_dir, "myvault", "API_KEY")
    scope = load_scope(scope_dir, "myvault")
    assert "API_KEY" in scope["allow"]


def test_add_allow_no_duplicates(scope_dir):
    add_allow(scope_dir, "myvault", "API_KEY")
    add_allow(scope_dir, "myvault", "API_KEY")
    scope = load_scope(scope_dir, "myvault")
    assert scope["allow"].count("API_KEY") == 1


def test_add_allow_removes_from_deny(scope_dir):
    add_deny(scope_dir, "myvault", "SECRET")
    add_allow(scope_dir, "myvault", "SECRET")
    scope = load_scope(scope_dir, "myvault")
    assert "SECRET" in scope["allow"]
    assert "SECRET" not in scope["deny"]


def test_add_deny_removes_from_allow(scope_dir):
    add_allow(scope_dir, "myvault", "TOKEN")
    add_deny(scope_dir, "myvault", "TOKEN")
    scope = load_scope(scope_dir, "myvault")
    assert "TOKEN" in scope["deny"]
    assert "TOKEN" not in scope["allow"]


def test_remove_rule_returns_true_when_found(scope_dir):
    add_allow(scope_dir, "myvault", "FOO")
    result = remove_rule(scope_dir, "myvault", "FOO")
    assert result is True
    scope = load_scope(scope_dir, "myvault")
    assert "FOO" not in scope["allow"]


def test_remove_rule_returns_false_when_not_found(scope_dir):
    result = remove_rule(scope_dir, "myvault", "NONEXISTENT")
    assert result is False


def test_apply_scope_empty_allow_passes_all():
    env = {"FOO": "1", "BAR": "2", "BAZ": "3"}
    scope = {"allow": [], "deny": []}
    assert apply_scope(env, scope) == env


def test_apply_scope_allow_list_filters():
    env = {"FOO": "1", "BAR": "2", "BAZ": "3"}
    scope = {"allow": ["FOO", "BAZ"], "deny": []}
    result = apply_scope(env, scope)
    assert result == {"FOO": "1", "BAZ": "3"}


def test_apply_scope_deny_list_excludes():
    env = {"FOO": "1", "BAR": "2", "BAZ": "3"}
    scope = {"allow": [], "deny": ["BAR"]}
    result = apply_scope(env, scope)
    assert "BAR" not in result
    assert "FOO" in result


def test_apply_scope_deny_takes_precedence_over_allow():
    env = {"FOO": "1", "BAR": "2"}
    scope = {"allow": ["FOO", "BAR"], "deny": ["BAR"]}
    result = apply_scope(env, scope)
    assert "BAR" not in result
    assert "FOO" in result


def test_apply_scope_empty_env():
    assert apply_scope({}, {"allow": ["FOO"], "deny": ["BAR"]}) == {}
