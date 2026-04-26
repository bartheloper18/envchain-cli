"""Tests for envchain.env_filter."""

import pytest
from envchain.env_filter import (
    FilterRule,
    apply_filters,
    filter_by_prefix,
    filter_by_regex,
    rename_keys,
)


SAMPLE_ENV = {
    "AWS_ACCESS_KEY_ID": "AKIA123",
    "AWS_SECRET_ACCESS_KEY": "secret",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_DEBUG": "true",
    "HOME": "/home/user",
}


# --- FilterRule ---

def test_filter_rule_matches_glob():
    rule = FilterRule("AWS_*")
    assert rule.matches("AWS_ACCESS_KEY_ID")
    assert not rule.matches("DB_HOST")


def test_filter_rule_transform_strips_prefix():
    rule = FilterRule("AWS_*", strip_prefix="AWS_")
    assert rule.transform_key("AWS_ACCESS_KEY_ID") == "ACCESS_KEY_ID"


def test_filter_rule_transform_adds_prefix():
    rule = FilterRule("DB_*", prefix="PROD_")
    assert rule.transform_key("DB_HOST") == "PROD_DB_HOST"


def test_filter_rule_transform_strip_and_add_prefix():
    rule = FilterRule("DB_*", prefix="PROD_", strip_prefix="DB_")
    assert rule.transform_key("DB_HOST") == "PROD_HOST"


# --- apply_filters ---

def test_apply_filters_empty_rules_returns_empty():
    result = apply_filters(SAMPLE_ENV, [])
    assert result == {}


def test_apply_filters_include_glob():
    rules = [FilterRule("AWS_*")]
    result = apply_filters(SAMPLE_ENV, rules)
    assert set(result.keys()) == {"AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"}


def test_apply_filters_exclude_rule():
    rules = [FilterRule("*"), FilterRule("HOME", exclude=True)]
    result = apply_filters(SAMPLE_ENV, rules)
    assert "HOME" not in result
    assert "AWS_ACCESS_KEY_ID" in result


def test_apply_filters_last_rule_wins():
    rules = [FilterRule("DB_*"), FilterRule("DB_HOST", exclude=True)]
    result = apply_filters(SAMPLE_ENV, rules)
    assert "DB_HOST" not in result
    assert "DB_PORT" in result


# --- filter_by_prefix ---

def test_filter_by_prefix_keeps_matching():
    result = filter_by_prefix(SAMPLE_ENV, "AWS_")
    assert set(result.keys()) == {"AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"}


def test_filter_by_prefix_strip():
    result = filter_by_prefix(SAMPLE_ENV, "AWS_", strip=True)
    assert "ACCESS_KEY_ID" in result
    assert "SECRET_ACCESS_KEY" in result
    assert "AWS_ACCESS_KEY_ID" not in result


def test_filter_by_prefix_no_match_returns_empty():
    result = filter_by_prefix(SAMPLE_ENV, "NONEXISTENT_")
    assert result == {}


# --- filter_by_regex ---

def test_filter_by_regex_include():
    result = filter_by_regex(SAMPLE_ENV, r"^DB_")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_by_regex_exclude():
    result = filter_by_regex(SAMPLE_ENV, r"^AWS_", exclude=True)
    assert "AWS_ACCESS_KEY_ID" not in result
    assert "DB_HOST" in result


# --- rename_keys ---

def test_rename_keys_renames_specified():
    mapping = {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}
    result = rename_keys(SAMPLE_ENV, mapping)
    assert "DATABASE_HOST" in result
    assert "DATABASE_PORT" in result
    assert result["DATABASE_HOST"] == "localhost"


def test_rename_keys_leaves_unspecified_unchanged():
    mapping = {"HOME": "USER_HOME"}
    result = rename_keys(SAMPLE_ENV, mapping)
    assert "AWS_ACCESS_KEY_ID" in result
    assert result["AWS_ACCESS_KEY_ID"] == "AKIA123"
