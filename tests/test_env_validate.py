"""Tests for envchain.env_validate."""

import pytest
from envchain.env_validate import (
    ValidationRule,
    validate_var,
    validate_vault,
    format_validation_results,
)


def test_validation_rule_invalid_action_raises():
    with pytest.raises(ValueError, match="Invalid action"):
        ValidationRule(key_pattern="FOO", action="ignore")


def test_validate_var_passes_when_value_present():
    rule = ValidationRule(key_pattern="FOO")
    result = validate_var("FOO", "bar", rule)
    assert result.passed


def test_validate_var_required_missing_fails():
    rule = ValidationRule(key_pattern="FOO", required=True)
    result = validate_var("FOO", None, rule)
    assert not result.passed
    assert "required" in result.message
    assert result.action == "error"


def test_validate_var_optional_missing_passes():
    rule = ValidationRule(key_pattern="FOO", required=False)
    result = validate_var("FOO", None, rule)
    assert result.passed


def test_validate_var_min_length_fail():
    rule = ValidationRule(key_pattern="FOO", min_length=8)
    result = validate_var("FOO", "short", rule)
    assert not result.passed
    assert "too short" in result.message


def test_validate_var_max_length_fail():
    rule = ValidationRule(key_pattern="FOO", max_length=4)
    result = validate_var("FOO", "toolongvalue", rule)
    assert not result.passed
    assert "too long" in result.message


def test_validate_var_regex_pass():
    rule = ValidationRule(key_pattern="PORT", regex=r"\d+")
    result = validate_var("PORT", "8080", rule)
    assert result.passed


def test_validate_var_regex_fail():
    rule = ValidationRule(key_pattern="PORT", regex=r"\d+", action="warn")
    result = validate_var("PORT", "not-a-number", rule)
    assert not result.passed
    assert "does not match pattern" in result.message
    assert result.action == "warn"


def test_validate_vault_matches_keys_by_pattern():
    env = {"AWS_KEY": "abc123", "AWS_SECRET": "xyz", "UNRELATED": "val"}
    rules = [ValidationRule(key_pattern=r"AWS_.*", min_length=5)]
    results = validate_vault(env, rules)
    keys = {r.key for r in results}
    assert "AWS_KEY" in keys
    assert "AWS_SECRET" in keys
    assert "UNRELATED" not in keys


def test_validate_vault_required_no_match_fails():
    env = {"OTHER": "val"}
    rules = [ValidationRule(key_pattern="MUST_EXIST", required=True)]
    results = validate_vault(env, rules)
    assert len(results) == 1
    assert not results[0].passed


def test_validate_vault_all_pass_returns_all_passed():
    env = {"TOKEN": "supersecret"}
    rules = [ValidationRule(key_pattern="TOKEN", min_length=5)]
    results = validate_vault(env, rules)
    assert all(r.passed for r in results)


def test_format_validation_results_all_pass():
    env = {"X": "hello"}
    rules = [ValidationRule(key_pattern="X")]
    results = validate_vault(env, rules)
    output = format_validation_results(results)
    assert output == "All validations passed."


def test_format_validation_results_shows_errors():
    env = {"SHORT": "ab"}
    rules = [ValidationRule(key_pattern="SHORT", min_length=10)]
    results = validate_vault(env, rules)
    output = format_validation_results(results)
    assert "[ERROR]" in output
    assert "too short" in output


def test_format_validation_results_shows_warn():
    env = {"VAL": "bad"}
    rules = [ValidationRule(key_pattern="VAL", regex=r"\d+", action="warn")]
    results = validate_vault(env, rules)
    output = format_validation_results(results)
    assert "[WARN]" in output
