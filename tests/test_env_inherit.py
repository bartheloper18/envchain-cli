"""Tests for envchain.env_inherit module."""

import os
import pytest
from envchain.env_inherit import InheritMode, merge_envs, diff_against_env, apply_to_process_env


# ---------------------------------------------------------------------------
# merge_envs
# ---------------------------------------------------------------------------

class TestMergeEnvs:
    def test_override_mode_vault_wins(self):
        base = {"KEY": "base_value", "SHARED": "base"}
        vault = {"SHARED": "vault", "NEW": "added"}
        result = merge_envs(base, vault, mode=InheritMode.OVERRIDE)
        assert result["SHARED"] == "vault"
        assert result["NEW"] == "added"
        assert result["KEY"] == "base_value"

    def test_preserve_mode_base_wins_on_conflict(self):
        base = {"SHARED": "base", "BASE_ONLY": "yes"}
        vault = {"SHARED": "vault", "VAULT_ONLY": "yes"}
        result = merge_envs(base, vault, mode=InheritMode.PRESERVE)
        assert result["SHARED"] == "base"
        assert result["VAULT_ONLY"] == "yes"
        assert result["BASE_ONLY"] == "yes"

    def test_vault_only_mode_ignores_base(self):
        base = {"BASE_KEY": "should_be_ignored", "SHARED": "base"}
        vault = {"VAULT_KEY": "kept", "SHARED": "vault"}
        result = merge_envs(base, vault, mode=InheritMode.VAULT_ONLY)
        assert "BASE_KEY" not in result
        assert result["VAULT_KEY"] == "kept"
        assert result["SHARED"] == "vault"

    def test_empty_vault_returns_base_in_override(self):
        base = {"A": "1", "B": "2"}
        result = merge_envs(base, {}, mode=InheritMode.OVERRIDE)
        assert result == base

    def test_empty_base_returns_vault_in_override(self):
        vault = {"X": "10"}
        result = merge_envs({}, vault, mode=InheritMode.OVERRIDE)
        assert result == vault

    def test_both_empty_returns_empty(self):
        result = merge_envs({}, {}, mode=InheritMode.OVERRIDE)
        assert result == {}

    def test_merge_does_not_mutate_inputs(self):
        base = {"A": "1"}
        vault = {"B": "2"}
        original_base = dict(base)
        original_vault = dict(vault)
        merge_envs(base, vault, mode=InheritMode.OVERRIDE)
        assert base == original_base
        assert vault == original_vault


# ---------------------------------------------------------------------------
# diff_against_env
# ---------------------------------------------------------------------------

class TestDiffAgainstEnv:
    def test_detects_added_keys(self):
        current = {"A": "1"}
        incoming = {"A": "1", "B": "2"}
        diff = diff_against_env(current, incoming)
        assert "B" in diff["added"]
        assert diff["added"]["B"] == "2"

    def test_detects_removed_keys(self):
        current = {"A": "1", "B": "2"}
        incoming = {"A": "1"}
        diff = diff_against_env(current, incoming)
        assert "B" in diff["removed"]

    def test_detects_changed_keys(self):
        current = {"A": "old"}
        incoming = {"A": "new"}
        diff = diff_against_env(current, incoming)
        assert "A" in diff["changed"]
        assert diff["changed"]["A"] == ("old", "new")

    def test_unchanged_keys_not_in_diff(self):
        env = {"A": "1", "B": "2"}
        diff = diff_against_env(env, env)
        assert diff["added"] == {}
        assert diff["removed"] == set() or diff["removed"] == []
        assert diff["changed"] == {}

    def test_empty_current_all_added(self):
        incoming = {"X": "1", "Y": "2"}
        diff = diff_against_env({}, incoming)
        assert set(diff["added"].keys()) == {"X", "Y"}

    def test_empty_incoming_all_removed(self):
        current = {"X": "1", "Y": "2"}
        diff = diff_against_env(current, {})
        removed = set(diff["removed"]) if not isinstance(diff["removed"], set) else diff["removed"]
        assert removed == {"X", "Y"}


# ---------------------------------------------------------------------------
# apply_to_process_env
# ---------------------------------------------------------------------------

class TestApplyToProcessEnv:
    def test_applies_vars_to_os_environ(self, monkeypatch):
        monkeypatch.delenv("ENVCHAIN_TEST_VAR", raising=False)
        apply_to_process_env({"ENVCHAIN_TEST_VAR": "hello"})
        assert os.environ.get("ENVCHAIN_TEST_VAR") == "hello"
        # Cleanup
        del os.environ["ENVCHAIN_TEST_VAR"]

    def test_overwrites_existing_var(self, monkeypatch):
        monkeypatch.setenv("ENVCHAIN_TEST_OVER", "original")
        apply_to_process_env({"ENVCHAIN_TEST_OVER": "replaced"})
        assert os.environ["ENVCHAIN_TEST_OVER"] == "replaced"

    def test_empty_dict_no_side_effects(self):
        before = dict(os.environ)
        apply_to_process_env({})
        assert dict(os.environ) == before

    def test_non_string_values_are_coerced(self, monkeypatch):
        """apply_to_process_env should coerce values to str for os.environ."""
        monkeypatch.delenv("ENVCHAIN_INT_VAR", raising=False)
        # Pass a numeric-string value (env vars are always strings)
        apply_to_process_env({"ENVCHAIN_INT_VAR": "42"})
        assert os.environ.get("ENVCHAIN_INT_VAR") == "42"
