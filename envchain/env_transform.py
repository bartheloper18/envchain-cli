"""Environment variable transformation pipeline.

Provides composable transformations that can be applied to environment
variable dictionaries before injection into shell sessions or processes.
Transformations include renaming, value substitution, case conversion,
and custom regex-based replacements.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional


class TransformType(str, Enum):
    RENAME = "rename"           # Rename a key to a new name
    PREFIX_ADD = "prefix_add"   # Add a prefix to all keys
    PREFIX_STRIP = "prefix_strip"  # Strip a prefix from matching keys
    UPPERCASE = "uppercase"     # Convert key to uppercase
    LOWERCASE = "lowercase"     # Convert key to lowercase
    VALUE_REPLACE = "value_replace"  # Regex replace in values
    VALUE_TEMPLATE = "value_template"  # Expand {OTHER_VAR} refs in values
    DROP = "drop"               # Remove a key entirely


@dataclass
class TransformRule:
    """A single transformation rule applied to an env dict."""

    transform_type: TransformType
    # Key selector: exact key name or glob pattern (None = apply to all)
    key_pattern: Optional[str] = None
    # For RENAME: new key name
    new_key: Optional[str] = None
    # For PREFIX_ADD / PREFIX_STRIP: the prefix string
    prefix: Optional[str] = None
    # For VALUE_REPLACE: regex pattern and replacement string
    value_regex: Optional[str] = None
    value_replacement: str = ""

    def __post_init__(self) -> None:
        if self.transform_type == TransformType.RENAME and not self.new_key:
            raise ValueError("RENAME transform requires 'new_key'")
        if self.transform_type in (TransformType.PREFIX_ADD, TransformType.PREFIX_STRIP):
            if not self.prefix:
                raise ValueError(f"{self.transform_type} transform requires 'prefix'")
        if self.transform_type == TransformType.VALUE_REPLACE and not self.value_regex:
            raise ValueError("VALUE_REPLACE transform requires 'value_regex'")


def _key_matches(key: str, pattern: Optional[str]) -> bool:
    """Return True if key matches the given glob-style pattern, or pattern is None."""
    if pattern is None:
        return True
    # Support simple glob: * matches anything
    regex = re.escape(pattern).replace(r"\*", ".*")
    return bool(re.fullmatch(regex, key))


def apply_transform(env: Dict[str, str], rule: TransformRule) -> Dict[str, str]:
    """Apply a single TransformRule to an env dict, returning a new dict."""
    result: Dict[str, str] = {}

    for key, value in env.items():
        matches = _key_matches(key, rule.key_pattern)

        if rule.transform_type == TransformType.DROP:
            if matches:
                continue  # Drop the key
            result[key] = value

        elif rule.transform_type == TransformType.RENAME:
            if matches and rule.new_key:
                result[rule.new_key] = value
            else:
                result[key] = value

        elif rule.transform_type == TransformType.PREFIX_ADD:
            new_k = f"{rule.prefix}{key}" if matches else key
            result[new_k] = value

        elif rule.transform_type == TransformType.PREFIX_STRIP:
            if matches and rule.prefix and key.startswith(rule.prefix):
                result[key[len(rule.prefix):]] = value
            else:
                result[key] = value

        elif rule.transform_type == TransformType.UPPERCASE:
            result[key.upper() if matches else key] = value

        elif rule.transform_type == TransformType.LOWERCASE:
            result[key.lower() if matches else key] = value

        elif rule.transform_type == TransformType.VALUE_REPLACE:
            if matches and rule.value_regex:
                value = re.sub(rule.value_regex, rule.value_replacement, value)
            result[key] = value

        elif rule.transform_type == TransformType.VALUE_TEMPLATE:
            if matches:
                # Expand {VAR_NAME} references using the current env snapshot
                value = re.sub(
                    r"\{([A-Za-z_][A-Za-z0-9_]*)\}",
                    lambda m: env.get(m.group(1), m.group(0)),
                    value,
                )
            result[key] = value

        else:
            result[key] = value

    return result


def apply_pipeline(
    env: Dict[str, str],
    rules: List[TransformRule],
) -> Dict[str, str]:
    """Apply an ordered list of TransformRules sequentially to an env dict."""
    for rule in rules:
        env = apply_transform(env, rule)
    return env


def build_transform_from_dict(data: dict) -> TransformRule:
    """Deserialise a TransformRule from a plain dict (e.g. loaded from JSON)."""
    return TransformRule(
        transform_type=TransformType(data["type"]),
        key_pattern=data.get("key_pattern"),
        new_key=data.get("new_key"),
        prefix=data.get("prefix"),
        value_regex=data.get("value_regex"),
        value_replacement=data.get("value_replacement", ""),
    )
