"""Audit log for vault access events."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

AUDIT_FILE = ".envchain_audit.log"


def _get_audit_path(vault_dir: str) -> Path:
    return Path(vault_dir) / AUDIT_FILE


def log_event(vault_dir: str, vault_name: str, action: str, details: str = "") -> None:
    """Append an audit event to the log file."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "vault": vault_name,
        "action": action,
        "user": os.environ.get("USER", "unknown"),
        "details": details,
    }
    audit_path = _get_audit_path(vault_dir)
    with open(audit_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def read_events(vault_dir: str, vault_name: str | None = None) -> list[dict]:
    """Read audit events, optionally filtered by vault name."""
    audit_path = _get_audit_path(vault_dir)
    if not audit_path.exists():
        return []
    events = []
    with open(audit_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if vault_name is None or entry.get("vault") == vault_name:
                    events.append(entry)
            except json.JSONDecodeError:
                continue
    return events


def format_events(events: list[dict]) -> str:
    """Format events for human-readable display."""
    if not events:
        return "No audit events found."
    lines = []
    for e in events:
        ts = e.get("timestamp", "?")
        vault = e.get("vault", "?")
        action = e.get("action", "?")
        user = e.get("user", "?")
        details = e.get("details", "")
        line = f"[{ts}] {user} {action} vault={vault}"
        if details:
            line += f" ({details})"
        lines.append(line)
    return "\n".join(lines)
