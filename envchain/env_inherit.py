"""env_inherit.py — Utilities for merging vault variables with the current
environment, supporting inheritance rules such as 'vault wins', 'env wins',
and 'merge' (vault fills gaps only).
"""

from __future__ import annotations

import os
from enum import Enum
from typing import Dict, Optional, Tuple


class InheritMode(str, Enum):
    """Controls how vault variables interact with existing environment variables."""

    VAULT_WINS = "vault_wins"   # vault values always override existing env vars
    ENV_WINS = "env_wins"       # existing env vars take precedence over vault values
    MERGE = "merge"             # vault fills in only keys absent from the environment


def merge_envs(
    vault_vars: Dict[str, str],
    current_env: Optional[Dict[str, str]] = None,
    mode: InheritMode = InheritMode.VAULT_WINS,
) -> Dict[str, str]:
    """Return a merged environment dictionary according to *mode*.

    Parameters
    ----------
    vault_vars:
        Key/value pairs loaded from the decrypted vault.
    current_env:
        The base environment to merge into.  Defaults to ``os.environ``.
    mode:
        One of the :class:`InheritMode` strategies.

    Returns
    -------
    dict
        A *new* dictionary representing the merged environment.  The caller's
        ``os.environ`` is never mutated by this function.
    """
    if current_env is None:
        current_env = dict(os.environ)

    if mode == InheritMode.VAULT_WINS:
        # Start with the current env and let vault values stomp on it.
        merged = {**current_env, **vault_vars}

    elif mode == InheritMode.ENV_WINS:
        # Start with vault values and let the current env stomp on them.
        merged = {**vault_vars, **current_env}

    elif mode == InheritMode.MERGE:
        # Only inject vault keys that are not already present.
        merged = dict(current_env)
        for key, value in vault_vars.items():
            if key not in merged:
                merged[key] = value

    else:  # pragma: no cover
        raise ValueError(f"Unknown InheritMode: {mode!r}")

    return merged


def diff_against_env(
    vault_vars: Dict[str, str],
    current_env: Optional[Dict[str, str]] = None,
) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
    """Compare vault variables against the current environment.

    Returns a three-tuple of ``(new, overridden, unchanged)`` where:

    * **new** – keys present in the vault but absent from the environment.
    * **overridden** – keys present in both but with differing values.
    * **unchanged** – keys present in both with identical values.

    Parameters
    ----------
    vault_vars:
        Key/value pairs from the vault.
    current_env:
        Environment to compare against.  Defaults to ``os.environ``.
    """
    if current_env is None:
        current_env = dict(os.environ)

    new: Dict[str, str] = {}
    overridden: Dict[str, str] = {}
    unchanged: Dict[str, str] = {}

    for key, value in vault_vars.items():
        if key not in current_env:
            new[key] = value
        elif current_env[key] != value:
            overridden[key] = value
        else:
            unchanged[key] = value

    return new, overridden, unchanged


def apply_to_process_env(
    vault_vars: Dict[str, str],
    mode: InheritMode = InheritMode.VAULT_WINS,
) -> None:
    """Mutate ``os.environ`` in-place using *merge_envs* with the given mode.

    This is the escape-hatch for callers that need the current process's
    environment updated (e.g. before ``exec``-ing a child process).

    Parameters
    ----------
    vault_vars:
        Key/value pairs to inject.
    mode:
        Merge strategy; see :class:`InheritMode`.
    """
    merged = merge_envs(vault_vars, mode=mode)
    # Only update/add keys — do not remove keys that exist solely in os.environ.
    for key, value in merged.items():
        os.environ[key] = value
