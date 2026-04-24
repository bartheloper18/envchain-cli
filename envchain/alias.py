"""Vault variable aliasing: map short names to vault:key references."""

import json
from pathlib import Path

ALIAS_FILENAME = "aliases.json"


def _get_alias_path(base_dir: str) -> Path:
    return Path(base_dir) / ALIAS_FILENAME


def load_aliases(base_dir: str) -> dict:
    """Load all aliases from the alias store."""
    path = _get_alias_path(base_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_aliases(base_dir: str, aliases: dict) -> None:
    """Persist aliases to disk."""
    path = _get_alias_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(aliases, f, indent=2)


def add_alias(base_dir: str, alias: str, vault: str, key: str) -> None:
    """Register an alias pointing to vault:key."""
    if not alias or not vault or not key:
        raise ValueError("alias, vault, and key must be non-empty strings")
    aliases = load_aliases(base_dir)
    aliases[alias] = {"vault": vault, "key": key}
    save_aliases(base_dir, aliases)


def remove_alias(base_dir: str, alias: str) -> bool:
    """Remove an alias. Returns True if it existed, False otherwise."""
    aliases = load_aliases(base_dir)
    if alias not in aliases:
        return False
    del aliases[alias]
    save_aliases(base_dir, aliases)
    return True


def resolve_alias(base_dir: str, alias: str) -> dict | None:
    """Return {vault, key} for the given alias, or None if not found."""
    aliases = load_aliases(base_dir)
    return aliases.get(alias)


def list_aliases(base_dir: str) -> list[dict]:
    """Return a list of all aliases with their targets."""
    aliases = load_aliases(base_dir)
    return [
        {"alias": name, "vault": info["vault"], "key": info["key"]}
        for name, info in sorted(aliases.items())
    ]
