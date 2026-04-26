"""Filter and transform environment variables before injection."""

from __future__ import annotations

import fnmatch
import re
from typing import Dict, List, Optional


class FilterRule:
    """A single filter rule with a pattern and optional transform."""

    def __init__(self, pattern: str, exclude: bool = False, prefix: str = "", strip_prefix: str = ""):
        self.pattern = pattern
        self.exclude = exclude
        self.prefix = prefix
        self.strip_prefix = strip_prefix

    def matches(self, key: str) -> bool:
        return fnmatch.fnmatch(key, self.pattern)

    def transform_key(self, key: str) -> str:
        if self.strip_prefix and key.startswith(self.strip_prefix):
            key = key[len(self.strip_prefix):]
        return self.prefix + key


def apply_filters(env: Dict[str, str], rules: List[FilterRule]) -> Dict[str, str]:
    """Apply a list of filter rules to an env dict, returning a filtered copy."""
    if not rules:
        return dict(env)

    result: Dict[str, str] = {}
    for key, value in env.items():
        matched_rule: Optional[FilterRule] = None
        for rule in rules:
            if rule.matches(key):
                matched_rule = rule
                # Last matching rule wins
        if matched_rule is None:
            continue
        if matched_rule.exclude:
            continue
        new_key = matched_rule.transform_key(key)
        result[new_key] = value
    return result


def filter_by_prefix(env: Dict[str, str], prefix: str, strip: bool = False) -> Dict[str, str]:
    """Keep only keys that start with *prefix*, optionally stripping it."""
    result: Dict[str, str] = {}
    for key, value in env.items():
        if key.startswith(prefix):
            new_key = key[len(prefix):] if strip else key
            if new_key:  # avoid empty key after stripping
                result[new_key] = value
    return result


def filter_by_regex(env: Dict[str, str], pattern: str, exclude: bool = False) -> Dict[str, str]:
    """Keep (or exclude) keys matching a regular expression."""
    compiled = re.compile(pattern)
    result: Dict[str, str] = {}
    for key, value in env.items():
        matched = bool(compiled.search(key))
        if matched != exclude:
            result[key] = value
    return result


def rename_keys(env: Dict[str, str], mapping: Dict[str, str]) -> Dict[str, str]:
    """Rename specific keys according to *mapping* (old_name -> new_name)."""
    result: Dict[str, str] = {}
    for key, value in env.items():
        new_key = mapping.get(key, key)
        result[new_key] = value
    return result
