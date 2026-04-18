"""Tests for envchain.audit module."""

import pytest
from pathlib import Path
from envchain.audit import log_event, read_events, format_events


@pytest.fixture
def audit_dir(tmp_path):
    return str(tmp_path)


def test_log_event_creates_file(audit_dir):
    log_event(audit_dir, "myvault", "GET", "API_KEY")
    audit_file = Path(audit_dir) / ".envchain_audit.log"
    assert audit_file.exists()


def test_log_event_content(audit_dir):
    log_event(audit_dir, "myvault", "SET", "DB_PASS")
    events = read_events(audit_dir)
    assert len(events) == 1
    assert events[0]["vault"] == "myvault"
    assert events[0]["action"] == "SET"
    assert events[0]["details"] == "DB_PASS"
    assert "timestamp" in events[0]
    assert "user" in events[0]


def test_multiple_events(audit_dir):
    log_event(audit_dir, "v1", "CREATE")
    log_event(audit_dir, "v2", "GET", "KEY")
    log_event(audit_dir, "v1", "GET", "SECRET")
    all_events = read_events(audit_dir)
    assert len(all_events) == 3


def test_filter_by_vault(audit_dir):
    log_event(audit_dir, "v1", "CREATE")
    log_event(audit_dir, "v2", "GET", "KEY")
    log_event(audit_dir, "v1", "GET", "SECRET")
    v1_events = read_events(audit_dir, vault_name="v1")
    assert len(v1_events) == 2
    assert all(e["vault"] == "v1" for e in v1_events)


def test_read_events_no_file(audit_dir):
    events = read_events(audit_dir)
    assert events == []


def test_format_events_empty():
    result = format_events([])
    assert result == "No audit events found."


def test_format_events_output(audit_dir):
    log_event(audit_dir, "myvault", "GET", "TOKEN")
    events = read_events(audit_dir)
    output = format_events(events)
    assert "myvault" in output
    assert "GET" in output
    assert "TOKEN" in output
