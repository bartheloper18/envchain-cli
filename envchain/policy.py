"""Access policy management for envchain vaults."""

import json
import os
from pathlib import Path
from typing import Optional

VALID_ACTIONS = {"read", "write", "delete", "export"}


def _get_policy_path(vault_name: str, base_dir: Optional[str] = None) -> Path:
    base = Path(base_dir) if base_dir else Path.home() / ".envchain"
    return base / vault_name / "policy.json"


def load_policy(vault_name: str, base_dir: Optional[str] = None) -> dict:
    path = _get_policy_path(vault_name, base_dir)
    if not path.exists():
        return {"rules": [], "default": "allow"}
    with open(path) as f:
        return json.load(f)


def save_policy(vault_name: str, policy: dict, base_dir: Optional[str] = None) -> None:
    path = _get_policy_path(vault_name, base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(policy, f, indent=2)


def add_rule(vault_name: str, action: str, key_pattern: str, effect: str = "deny",
             base_dir: Optional[str] = None) -> None:
    if action not in VALID_ACTIONS:
        raise ValueError(f"Invalid action '{action}'. Must be one of: {VALID_ACTIONS}")
    if effect not in ("allow", "deny"):
        raise ValueError("Effect must be 'allow' or 'deny'")
    policy = load_policy(vault_name, base_dir)
    rule = {"action": action, "key_pattern": key_pattern, "effect": effect}
    if rule not in policy["rules"]:
        policy["rules"].append(rule)
    save_policy(vault_name, policy, base_dir)


def remove_rule(vault_name: str, action: str, key_pattern: str,
                base_dir: Optional[str] = None) -> bool:
    policy = load_policy(vault_name, base_dir)
    original_len = len(policy["rules"])
    policy["rules"] = [
        r for r in policy["rules"]
        if not (r["action"] == action and r["key_pattern"] == key_pattern)
    ]
    if len(policy["rules"]) < original_len:
        save_policy(vault_name, policy, base_dir)
        return True
    return False


def is_allowed(vault_name: str, action: str, key: str,
               base_dir: Optional[str] = None) -> bool:
    import fnmatch
    policy = load_policy(vault_name, base_dir)
    for rule in policy["rules"]:
        if rule["action"] == action and fnmatch.fnmatch(key, rule["key_pattern"]):
            return rule["effect"] == "allow"
    return policy.get("default", "allow") == "allow"


def set_default(vault_name: str, effect: str, base_dir: Optional[str] = None) -> None:
    if effect not in ("allow", "deny"):
        raise ValueError("Effect must be 'allow' or 'deny'")
    policy = load_policy(vault_name, base_dir)
    policy["default"] = effect
    save_policy(vault_name, policy, base_dir)
