"""Tests for envchain.hooks."""
import pytest
from unittest.mock import patch
from pathlib import Path
import json
from envchain.hooks import (
    register_hook, remove_hook, list_hooks, run_hooks,
    load_hooks, save_hooks, HOOK_EVENTS
)


@pytest.fixture
def hook_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envchain.hooks.HOOKS_DIR", tmp_path)
    return tmp_path


def test_register_hook_creates_entry(hook_dir):
    register_hook("myvault", "post-unlock", "echo unlocked")
    hooks = load_hooks("myvault")
    assert "echo unlocked" in hooks["post-unlock"]


def test_register_hook_no_duplicates(hook_dir):
    register_hook("myvault", "post-unlock", "echo hi")
    register_hook("myvault", "post-unlock", "echo hi")
    hooks = load_hooks("myvault")
    assert hooks["post-unlock"].count("echo hi") == 1


def test_register_invalid_event_raises(hook_dir):
    with pytest.raises(ValueError, match="Unknown event"):
        register_hook("myvault", "bad-event", "echo x")


def test_remove_hook_returns_true(hook_dir):
    register_hook("myvault", "pre-lock", "echo bye")
    result = remove_hook("myvault", "pre-lock", "echo bye")
    assert result is True
    hooks = load_hooks("myvault")
    assert "echo bye" not in hooks.get("pre-lock", [])


def test_remove_nonexistent_hook_returns_false(hook_dir):
    result = remove_hook("myvault", "pre-lock", "echo nothing")
    assert result is False


def test_list_hooks_empty(hook_dir):
    hooks = list_hooks("empty_vault")
    assert hooks == {}


def test_list_hooks_multiple_events(hook_dir):
    register_hook("v", "post-unlock", "cmd1")
    register_hook("v", "pre-lock", "cmd2")
    hooks = list_hooks("v")
    assert "cmd1" in hooks["post-unlock"]
    assert "cmd2" in hooks["pre-lock"]


def test_run_hooks_success(hook_dir):
    register_hook("v", "post-set", "echo hello")
    results = run_hooks("v", "post-set")
    assert len(results) == 1
    assert results[0]["returncode"] == 0
    assert results[0]["stdout"] == "hello"


def test_run_hooks_no_hooks_returns_empty(hook_dir):
    results = run_hooks("v", "post-unlock")
    assert results == []


def test_run_hooks_failed_command(hook_dir):
    register_hook("v", "pre-set", "exit 1")
    results = run_hooks("v", "pre-set")
    assert results[0]["returncode"] != 0
