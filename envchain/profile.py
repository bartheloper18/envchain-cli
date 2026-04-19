"""Profile management: named sets of vaults to load together."""

import json
from pathlib import Path

DEFAULT_PROFILES_DIR = Path.home() / ".envchain" / "profiles"


def _get_profile_path(profiles_dir: Path, name: str) -> Path:
    return profiles_dir / f"{name}.json"


def create_profile(name: str, vaults: list[str], profiles_dir: Path = DEFAULT_PROFILES_DIR) -> Path:
    profiles_dir.mkdir(parents=True, exist_ok=True)
    path = _get_profile_path(profiles_dir, name)
    if path.exists():
        raise FileExistsError(f"Profile '{name}' already exists.")
    path.write_text(json.dumps({"name": name, "vaults": vaults}, indent=2))
    return path


def load_profile(name: str, profiles_dir: Path = DEFAULT_PROFILES_DIR) -> dict:
    path = _get_profile_path(profiles_dir, name)
    if not path.exists():
        raise FileNotFoundError(f"Profile '{name}' not found.")
    return json.loads(path.read_text())


def save_profile(name: str, data: dict, profiles_dir: Path = DEFAULT_PROFILES_DIR) -> None:
    profiles_dir.mkdir(parents=True, exist_ok=True)
    path = _get_profile_path(profiles_dir, name)
    path.write_text(json.dumps(data, indent=2))


def delete_profile(name: str, profiles_dir: Path = DEFAULT_PROFILES_DIR) -> bool:
    path = _get_profile_path(profiles_dir, name)
    if not path.exists():
        return False
    path.unlink()
    return True


def list_profiles(profiles_dir: Path = DEFAULT_PROFILES_DIR) -> list[str]:
    if not profiles_dir.exists():
        return []
    return [p.stem for p in sorted(profiles_dir.glob("*.json"))]


def add_vault_to_profile(name: str, vault: str, profiles_dir: Path = DEFAULT_PROFILES_DIR) -> None:
    data = load_profile(name, profiles_dir)
    if vault not in data["vaults"]:
        data["vaults"].append(vault)
    save_profile(name, data, profiles_dir)


def remove_vault_from_profile(name: str, vault: str, profiles_dir: Path = DEFAULT_PROFILES_DIR) -> bool:
    data = load_profile(name, profiles_dir)
    if vault not in data["vaults"]:
        return False
    data["vaults"].remove(vault)
    save_profile(name, data, profiles_dir)
    return True
