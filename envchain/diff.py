"""Vault diff: compare two vaults or two snapshots of the same vault."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class DiffResult:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    unchanged: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def diff_vaults(
    old: Dict[str, str],
    new: Dict[str, str],
    *,
    show_values: bool = False,
) -> DiffResult:
    """Compare two env-var dicts and return a DiffResult.

    Args:
        old: Mapping from the baseline vault.
        new: Mapping from the target vault.
        show_values: When False, changed values are masked with '***'.
    """
    result = DiffResult()

    old_keys = set(old)
    new_keys = set(new)

    for key in sorted(new_keys - old_keys):
        result.added[key] = new[key] if show_values else "***"

    for key in sorted(old_keys - new_keys):
        result.removed[key] = old[key] if show_values else "***"

    for key in sorted(old_keys & new_keys):
        if old[key] != new[key]:
            if show_values:
                result.changed[key] = (old[key], new[key])
            else:
                result.changed[key] = ("***", "***")
        else:
            result.unchanged.append(key)

    return result


def format_diff(result: DiffResult, *, show_values: bool = False) -> str:
    """Render a DiffResult as a human-readable string."""
    lines: List[str] = []

    for key, val in result.added.items():
        lines.append(f"+ {key}={val}" if show_values else f"+ {key}")

    for key, val in result.removed.items():
        lines.append(f"- {key}={val}" if show_values else f"- {key}")

    for key, (old_val, new_val) in result.changed.items():
        if show_values:
            lines.append(f"~ {key}: {old_val!r} -> {new_val!r}")
        else:
            lines.append(f"~ {key}")

    if not lines:
        return "No differences found."

    return "\n".join(lines)
