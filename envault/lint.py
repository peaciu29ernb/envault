"""Lint/validate .env variable names and values against common rules."""

import re
from typing import Dict, List

# Valid POSIX env var name: starts with letter or underscore, then alphanumeric/underscore
_VALID_NAME_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

# Warn if value looks like it contains an unquoted shell special character
_SUSPICIOUS_VALUE_RE = re.compile(r'[\$`!;|&<>]')


class LintWarning:
    def __init__(self, key: str, message: str, severity: str = "warning"):
        self.key = key
        self.message = message
        self.severity = severity  # "warning" or "error"

    def __repr__(self):
        return f"[{self.severity.upper()}] {self.key}: {self.message}"

    def to_dict(self):
        return {"key": self.key, "message": self.message, "severity": self.severity}


def lint_env(env: Dict[str, str]) -> List[LintWarning]:
    """Lint an env dict and return a list of LintWarning objects."""
    warnings: List[LintWarning] = []

    for key, value in env.items():
        # Check key naming convention
        if not _VALID_NAME_RE.match(key):
            warnings.append(LintWarning(key, "Key is not a valid POSIX variable name.", "error"))

        # Warn about lowercase keys (convention: env vars are uppercase)
        if key != key.upper():
            warnings.append(LintWarning(key, "Key is not uppercase (convention).", "warning"))

        # Warn about empty values
        if value == "":
            warnings.append(LintWarning(key, "Value is empty.", "warning"))

        # Warn about suspiciously long values (possible accidental paste)
        if len(value) > 1024:
            warnings.append(LintWarning(key, f"Value is very long ({len(value)} chars).", "warning"))

        # Warn about suspicious shell characters in value
        if _SUSPICIOUS_VALUE_RE.search(value):
            warnings.append(LintWarning(key, "Value contains shell special characters.", "warning"))

        # Warn about leading/trailing whitespace
        if value != value.strip():
            warnings.append(LintWarning(key, "Value has leading or trailing whitespace.", "warning"))

    return warnings


def format_lint_report(warnings: List[LintWarning]) -> str:
    """Return a human-readable lint report string."""
    if not warnings:
        return "No lint issues found."
    lines = [f"Found {len(warnings)} issue(s):"] + [f"  {w}" for w in warnings]
    return "\n".join(lines)


def has_errors(warnings: List[LintWarning]) -> bool:
    """Return True if any warning is of severity 'error'."""
    return any(w.severity == "error" for w in warnings)
