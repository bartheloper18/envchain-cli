"""Tag management for vault variables."""

import json
from pathlib import Path


def _get_tags_path(vault_name: str, base_dir: str = None) -> Path:
    base = Path(base_dir) if base_dir else Path.home() / ".envchain"
    return base / vault_name / "tags.json"


def load_tags(vault_name: str, base_dir: str = None) -> dict:
    """Load tags mapping {var_key: [tag, ...]} for a vault."""
    path = _get_tags_path(vault_name, base_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Corrupted tags file for vault '{vault_name}': {e}") from e


def save_tags(vault_name: str, tags: dict, base_dir: str = None) -> None:
    """Persist tags mapping for a vault."""
    path = _get_tags_path(vault_name, base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(tags, f, indent=2)


def add_tag(vault_name: str, key: str, tag: str, base_dir: str = None) -> None:
    """Add a tag to a variable key."""
    tags = load_tags(vault_name, base_dir)
    tags.setdefault(key, [])
    if tag not in tags[key]:
        tags[key].append(tag)
    save_tags(vault_name, tags, base_dir)


def remove_tag(vault_name: str, key: str, tag: str, base_dir: str = None) -> None:
    """Remove a tag from a variable key."""
    tags = load_tags(vault_name, base_dir)
    if key in tags and tag in tags[key]:
        tags[key].remove(tag)
        if not tags[key]:
            del tags[key]
    save_tags(vault_name, tags, base_dir)


def get_tags(vault_name: str, key: str, base_dir: str = None) -> list:
    """Return tags for a specific variable key."""
    return load_tags(vault_name, base_dir).get(key, [])


def find_by_tag(vault_name: str, tag: str, base_dir: str = None) -> list:
    """Return all variable keys that have the given tag."""
    tags = load_tags(vault_name, base_dir)
    return [key for key, key_tags in tags.items() if tag in key_tags]


def list_all_tags(vault_name: str, base_dir: str = None) -> list:
    """Return sorted list of all unique tags used in a vault."""
    tags = load_tags(vault_name, base_dir)
    unique = set(t for key_tags in tags.values() for t in key_tags)
    return sorted(unique)
