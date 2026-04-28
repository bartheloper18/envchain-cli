"""Validation rules for environment variables stored in vaults."""

import re
from dataclasses import dataclass, field
from typing import Optional


VALID_ACTIONS = ("warn", "error")


@dataclass
class ValidationRule:
    key_pattern: str
    required: bool = False
    regex: Optional[str] = None
    min_length: int = 0
    max_length: int = 0
    action: str = "error"

    def __post_init__(self):
        if self.action not in VALID_ACTIONS:
            raise ValueError(f"Invalid action '{self.action}'. Must be one of {VALID_ACTIONS}")


@dataclass
class ValidationResult:
    key: str
    passed: bool
    message: str = ""
    action: str = "error"


def validate_var(key: str, value: Optional[str], rule: ValidationRule) -> ValidationResult:
    """Validate a single variable against a rule."""
    if value is None:
        if rule.required:
            return ValidationResult(key, False, f"'{key}' is required but missing.", rule.action)
        return ValidationResult(key, True)

    if rule.min_length and len(value) < rule.min_length:
        return ValidationResult(
            key, False,
            f"'{key}' is too short (min {rule.min_length}, got {len(value)}).",
            rule.action,
        )

    if rule.max_length and len(value) > rule.max_length:
        return ValidationResult(
            key, False,
            f"'{key}' is too long (max {rule.max_length}, got {len(value)}).",
            rule.action,
        )

    if rule.regex and not re.fullmatch(rule.regex, value):
        return ValidationResult(
            key, False,
            f"'{key}' does not match pattern '{rule.regex}'.",
            rule.action,
        )

    return ValidationResult(key, True)


def validate_vault(env: dict, rules: list[ValidationRule]) -> list[ValidationResult]:
    """Validate all variables in an env dict against a list of rules."""
    results = []
    for rule in rules:
        matched_keys = [
            k for k in env
            if re.fullmatch(rule.key_pattern, k)
        ]
        if not matched_keys:
            if rule.required:
                results.append(ValidationResult(
                    rule.key_pattern, False,
                    f"No keys matching '{rule.key_pattern}' found (required).",
                    rule.action,
                ))
        else:
            for key in matched_keys:
                results.append(validate_var(key, env.get(key), rule))
    return results


def format_validation_results(results: list[ValidationResult]) -> str:
    """Format validation results as a human-readable string."""
    lines = []
    for r in results:
        if not r.passed:
            prefix = "[ERROR]" if r.action == "error" else "[WARN] "
            lines.append(f"{prefix} {r.message}")
    if not lines:
        return "All validations passed."
    return "\n".join(lines)
