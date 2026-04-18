"""Shell export utilities for injecting environment variables."""

import os
import subprocess
from typing import Dict, Optional


SUPPORTED_SHELLS = ["bash", "zsh", "fish", "sh"]


def detect_shell() -> str:
    """Detect the current shell from environment."""
    shell = os.environ.get("SHELL", "/bin/sh")
    name = os.path.basename(shell)
    if name in SUPPORTED_SHELLS:
        return name
    return "sh"


def format_exports(variables: Dict[str, str], shell: Optional[str] = None) -> str:
    """Format variables as export statements for the given shell.

    Args:
        variables: Dictionary of variable name to value.
        shell: Target shell. Defaults to detected shell.

    Returns:
        A string of export statements suitable for eval.
    """
    if shell is None:
        shell = detect_shell()

    if shell == "fish":
        lines = [
            "set -x {} {};".format(k, _quote_fish(v))
            for k, v in variables.items()
        ]
    else:
        lines = [
            "export {}={};".format(k, _quote_posix(v))
            for k, v in variables.items()
        ]

    return "\n".join(lines)


def _quote_posix(value: str) -> str:
    """Single-quote a value for POSIX shells, escaping single quotes."""
    escaped = value.replace("'", "'\"'\"'")
    return "'{}'".format(escaped)


def _quote_fish(value: str) -> str:
    """Quote a value for fish shell."""
    escaped = value.replace("'", "\\'")
    return "'{}'".format(escaped)


def inject_into_env(variables: Dict[str, str]) -> None:
    """Inject variables into the current process environment.

    Args:
        variables: Dictionary of variable name to value.
    """
    for key, value in variables.items():
        os.environ[key] = value
