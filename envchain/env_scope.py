"""Environment variable scoping: restrict which vars are visible per vault or context."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_SCOPE_FILENAME = ".scope.json"


def _get_scope_path(vault_dir: str, vault_name: str) -> Path:
    return Path(vault_dir) / vault_name / _SCOPE_FILENAME


def load_scope(vault_dir: str, vault_name: str) -> Dict[str, List[str]]:
    """Load scope rules for a vault. Returns dict with 'allow' and 'deny' lists."""
    path = _get_scope_path(vault_dir, vault_name)
    if not path.exists():
        return {"allow": [], "deny": []}
    with open(path, "r") as f:
        data = json.load(f)
    return {
        "allow": data.get("allow", []),
        "deny": data.get("deny", []),
    }


def save_scope(vault_dir: str, vault_name: str, scope: Dict[str, List[str]]) -> None:
    """Persist scope rules for a vault."""
    path = _get_scope_path(vault_dir, vault_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(scope, f, indent=2)


def add_allow(vault_dir: str, vault_name: str, key: str) -> None:
    """Add a key to the allow list, removing it from deny if present."""
    scope = load_scope(vault_dir, vault_name)
    if key not in scope["allow"]:
        scope["allow"].append(key)
    if key in scope["deny"]:
        scope["deny"].remove(key)
    save_scope(vault_dir, vault_name, scope)


def add_deny(vault_dir: str, vault_name: str, key: str) -> None:
    """Add a key to the deny list, removing it from allow if present."""
    scope = load_scope(vault_dir, vault_name)
    if key not in scope["deny"]:
        scope["deny"].append(key)
    if key in scope["allow"]:
        scope["allow"].remove(key)
    save_scope(vault_dir, vault_name, scope)


def remove_rule(vault_dir: str, vault_name: str, key: str) -> bool:
    """Remove a key from both allow and deny lists. Returns True if anything changed."""
    scope = load_scope(vault_dir, vault_name)
    changed = False
    for lst in ("allow", "deny"):
        if key in scope[lst]:
            scope[lst].remove(key)
            changed = True
    if changed:
        save_scope(vault_dir, vault_name, scope)
    return changed


def apply_scope(env: Dict[str, str], scope: Dict[str, List[str]]) -> Dict[str, str]:
    """Filter an env dict according to allow/deny rules.

    - If allow list is non-empty, only those keys pass through.
    - Keys in deny list are always excluded.
    - An empty allow list means all keys are allowed (subject to deny).
    """
    allow: List[str] = scope.get("allow", [])
    deny: List[str] = scope.get("deny", [])

    result: Dict[str, str] = {}
    for key, value in env.items():
        if key in deny:
            continue
        if allow and key not in allow:
            continue
        result[key] = value
    return result
