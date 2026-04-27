"""Template rendering: substitute vault variables into string templates."""

import re
from typing import Dict, Optional

_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


def render_template(template: str, variables: Dict[str, str], strict: bool = False) -> str:
    """Substitute ${VAR} or $VAR placeholders with values from variables dict.

    Args:
        template: String containing placeholders.
        variables: Mapping of variable names to values.
        strict: If True, raise KeyError for missing variables.

    Returns:
        Rendered string.
    """
    def replacer(match: re.Match) -> str:
        key = match.group(1) or match.group(2)
        if key in variables:
            return variables[key]
        if strict:
            raise KeyError(f"Variable '{key}' not found in vault")
        return match.group(0)

    return _PATTERN.sub(replacer, template)


def find_placeholders(template: str) -> list[str]:
    """Return a sorted, deduplicated list of placeholder names in the template."""
    found = set()
    for match in _PATTERN.finditer(template):
        found.add(match.group(1) or match.group(2))
    return sorted(found)


def find_missing_variables(template: str, variables: Dict[str, str]) -> list[str]:
    """Return a sorted list of placeholder names that are not present in variables.

    Useful for validating that all required variables are available before
    performing a strict render.

    Args:
        template: String containing placeholders.
        variables: Mapping of variable names to values.

    Returns:
        Sorted list of placeholder names missing from variables.
    """
    placeholders = find_placeholders(template)
    return sorted(name for name in placeholders if name not in variables)


def render_file(src_path: str, dst_path: str, variables: Dict[str, str], strict: bool = False) -> None:
    """Read a template file, render it, and write to dst_path."""
    with open(src_path, "r") as f:
        content = f.read()
    rendered = render_template(content, variables, strict=strict)
    with open(dst_path, "w") as f:
        f.write(rendered)
