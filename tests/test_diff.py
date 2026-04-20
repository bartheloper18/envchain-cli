"""Tests for envchain.diff."""

from __future__ import annotations

import pytest

from envchain.diff import DiffResult, diff_vaults, format_diff


OLD = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "old_secret"}
NEW = {"DB_HOST": "prod.db", "DB_PORT": "5432", "API_KEY": "abc123"}


# ---------------------------------------------------------------------------
# diff_vaults
# ---------------------------------------------------------------------------

def test_diff_detects_added_keys():
    result = diff_vaults(OLD, NEW)
    assert "API_KEY" in result.added


def test_diff_detects_removed_keys():
    result = diff_vaults(OLD, NEW)
    assert "SECRET" in result.removed


def test_diff_detects_changed_keys():
    result = diff_vaults(OLD, NEW)
    assert "DB_HOST" in result.changed


def test_diff_detects_unchanged_keys():
    result = diff_vaults(OLD, NEW)
    assert "DB_PORT" in result.unchanged


def test_diff_masks_values_by_default():
    result = diff_vaults(OLD, NEW)
    assert result.added["API_KEY"] == "***"
    assert result.removed["SECRET"] == "***"
    old_val, new_val = result.changed["DB_HOST"]
    assert old_val == "***"
    assert new_val == "***"


def test_diff_shows_values_when_requested():
    result = diff_vaults(OLD, NEW, show_values=True)
    assert result.added["API_KEY"] == "abc123"
    assert result.removed["SECRET"] == "old_secret"
    old_val, new_val = result.changed["DB_HOST"]
    assert old_val == "localhost"
    assert new_val == "prod.db"


def test_diff_identical_vaults_no_changes():
    result = diff_vaults(OLD, OLD)
    assert not result.has_changes
    assert set(result.unchanged) == set(OLD.keys())


def test_diff_empty_old():
    result = diff_vaults({}, NEW)
    assert set(result.added.keys()) == set(NEW.keys())
    assert not result.removed


def test_diff_empty_new():
    result = diff_vaults(OLD, {})
    assert set(result.removed.keys()) == set(OLD.keys())
    assert not result.added


# ---------------------------------------------------------------------------
# format_diff
# ---------------------------------------------------------------------------

def test_format_diff_no_changes():
    result = diff_vaults(OLD, OLD)
    assert format_diff(result) == "No differences found."


def test_format_diff_added_prefix():
    result = diff_vaults({}, {"FOO": "bar"})
    output = format_diff(result)
    assert output.startswith("+")


def test_format_diff_removed_prefix():
    result = diff_vaults({"FOO": "bar"}, {})
    output = format_diff(result)
    assert output.startswith("-")


def test_format_diff_changed_prefix():
    result = diff_vaults({"FOO": "old"}, {"FOO": "new"})
    output = format_diff(result)
    assert output.startswith("~")


def test_format_diff_show_values_contains_arrow():
    result = diff_vaults({"FOO": "old"}, {"FOO": "new"}, show_values=True)
    output = format_diff(result, show_values=True)
    assert "->" in output
