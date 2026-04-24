"""Tests for envchain.policy module."""

import pytest
from envchain.policy import (
    add_rule, remove_rule, is_allowed, load_policy,
    save_policy, set_default
)


@pytest.fixture
def policy_dir(tmp_path):
    return str(tmp_path)


def test_load_policy_default_when_missing(policy_dir):
    policy = load_policy("myvault", base_dir=policy_dir)
    assert policy["default"] == "allow"
    assert policy["rules"] == []


def test_add_rule_creates_entry(policy_dir):
    add_rule("myvault", "read", "SECRET_*", effect="deny", base_dir=policy_dir)
    policy = load_policy("myvault", base_dir=policy_dir)
    assert len(policy["rules"]) == 1
    assert policy["rules"][0] == {"action": "read", "key_pattern": "SECRET_*", "effect": "deny"}


def test_add_rule_no_duplicates(policy_dir):
    add_rule("myvault", "write", "DB_*", effect="deny", base_dir=policy_dir)
    add_rule("myvault", "write", "DB_*", effect="deny", base_dir=policy_dir)
    policy = load_policy("myvault", base_dir=policy_dir)
    assert len(policy["rules"]) == 1


def test_add_rule_invalid_action_raises(policy_dir):
    with pytest.raises(ValueError, match="Invalid action"):
        add_rule("myvault", "fly", "KEY", base_dir=policy_dir)


def test_add_rule_invalid_effect_raises(policy_dir):
    with pytest.raises(ValueError, match="Effect must be"):
        add_rule("myvault", "read", "KEY", effect="maybe", base_dir=policy_dir)


def test_remove_rule_returns_true_on_success(policy_dir):
    add_rule("myvault", "delete", "TEMP_*", base_dir=policy_dir)
    result = remove_rule("myvault", "delete", "TEMP_*", base_dir=policy_dir)
    assert result is True
    policy = load_policy("myvault", base_dir=policy_dir)
    assert policy["rules"] == []


def test_remove_rule_returns_false_when_not_found(policy_dir):
    result = remove_rule("myvault", "read", "NONEXISTENT", base_dir=policy_dir)
    assert result is False


def test_is_allowed_default_allow(policy_dir):
    assert is_allowed("myvault", "read", "MY_KEY", base_dir=policy_dir) is True


def test_is_allowed_deny_rule_matches(policy_dir):
    add_rule("myvault", "read", "SECRET_*", effect="deny", base_dir=policy_dir)
    assert is_allowed("myvault", "read", "SECRET_TOKEN", base_dir=policy_dir) is False


def test_is_allowed_deny_rule_no_match(policy_dir):
    add_rule("myvault", "read", "SECRET_*", effect="deny", base_dir=policy_dir)
    assert is_allowed("myvault", "read", "PUBLIC_KEY", base_dir=policy_dir) is True


def test_set_default_deny(policy_dir):
    set_default("myvault", "deny", base_dir=policy_dir)
    assert is_allowed("myvault", "read", "ANY_KEY", base_dir=policy_dir) is False


def test_set_default_invalid_raises(policy_dir):
    with pytest.raises(ValueError, match="Effect must be"):
        set_default("myvault", "maybe", base_dir=policy_dir)


def test_allow_rule_overrides_deny_default(policy_dir):
    set_default("myvault", "deny", base_dir=policy_dir)
    add_rule("myvault", "read", "PUBLIC_*", effect="allow", base_dir=policy_dir)
    assert is_allowed("myvault", "read", "PUBLIC_INFO", base_dir=policy_dir) is True
    assert is_allowed("myvault", "read", "PRIVATE_KEY", base_dir=policy_dir) is False
