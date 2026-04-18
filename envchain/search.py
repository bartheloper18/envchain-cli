"""Search and filter environment variables across vaults."""

from __future__ import annotations

from typing import Optional

from envchain.vault import load_vault


def search_vars(
    vault_name: str,
    password: str,
    pattern: str,
    keys_only: bool = False,
) -> list[dict]:
    """Search for variables matching *pattern* (case-insensitive substring).

    Returns a list of dicts with keys 'vault', 'key', and optionally 'value'.
    """
    vault = load_vault(vault_name, password)
    results = []
    pattern_lower = pattern.lower()
    for key, value in vault.items():
        if pattern_lower in key.lower() or (
            not keys_only and pattern_lower in value.lower()
        ):
            entry = {"vault": vault_name, "key": key}
            if not keys_only:
                entry["value"] = value
            results.append(entry)
    return results


def search_all_vaults(
    vault_names: list[str],
    password: str,
    pattern: str,
    keys_only: bool = False,
) -> list[dict]:
    """Search across multiple vaults, skipping vaults that fail to decrypt."""
    results = []
    for name in vault_names:
        try:
            results.extend(search_vars(name, password, pattern, keys_only))
        except Exception:
            continue
    return results


def format_results(results: list[dict], show_values: bool = True) -> str:
    """Format search results for display."""
    if not results:
        return "No matches found."
    lines = []
    for entry in results:
        if show_values and "value" in entry:
            lines.append(f"[{entry['vault']}] {entry['key']} = {entry['value']}")
        else:
            lines.append(f"[{entry['vault']}] {entry['key']}")
    return "\n".join(lines)
