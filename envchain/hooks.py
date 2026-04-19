"""Pre/post hooks for vault operations."""
import json
import os
import subprocess
from pathlib import Path

HOOKS_DIR = Path.home() / ".envchain" / "hooks"

HOOK_EVENTS = ["pre-unlock", "post-unlock", "pre-lock", "post-lock", "pre-set", "post-set"]


def _get_hooks_path(vault_name: str) -> Path:
    return HOOKS_DIR / f"{vault_name}.json"


def load_hooks(vault_name: str) -> dict:
    path = _get_hooks_path(vault_name)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_hooks(vault_name: str, hooks: dict) -> None:
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    with open(_get_hooks_path(vault_name), "w") as f:
        json.dump(hooks, f, indent=2)


def register_hook(vault_name: str, event: str, command: str) -> None:
    if event not in HOOK_EVENTS:
        raise ValueError(f"Unknown event '{event}'. Valid events: {HOOK_EVENTS}")
    hooks = load_hooks(vault_name)
    hooks.setdefault(event, [])
    if command not in hooks[event]:
        hooks[event].append(command)
    save_hooks(vault_name, hooks)


def remove_hook(vault_name: str, event: str, command: str) -> bool:
    hooks = load_hooks(vault_name)
    cmds = hooks.get(event, [])
    if command not in cmds:
        return False
    cmds.remove(command)
    hooks[event] = cmds
    save_hooks(vault_name, hooks)
    return True


def run_hooks(vault_name: str, event: str, env: dict = None) -> list:
    hooks = load_hooks(vault_name)
    results = []
    for cmd in hooks.get(event, []):
        merged_env = {**os.environ, **(env or {})}
        result = subprocess.run(cmd, shell=True, env=merged_env, capture_output=True, text=True)
        results.append({"command": cmd, "returncode": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()})
    return results


def list_hooks(vault_name: str) -> dict:
    return load_hooks(vault_name)
