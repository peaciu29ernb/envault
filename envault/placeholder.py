"""Placeholder detection and reporting for .env files.

Identifies keys whose values look like unfilled template placeholders,
such as <MY_VAR>, {{MY_VAR}}, ${MY_VAR}, CHANGEME, TODO, etc.
"""

import re
from typing import Dict, List

# Patterns that indicate a value is a placeholder / not yet filled in
_PLACEHOLDER_PATTERNS = [
    re.compile(r'^<[^>]+>$'),           # <VALUE>
    re.compile(r'^\{\{[^}]+\}\}$'),    # {{VALUE}}
    re.compile(r'^\$\{[^}]+\}$'),      # ${VALUE}
    re.compile(r'^%[^%]+%$'),           # %VALUE%
    re.compile(r'^CHANGEME$', re.I),
    re.compile(r'^TODO$', re.I),
    re.compile(r'^REPLACE_ME$', re.I),
    re.compile(r'^YOUR_[A-Z_]+$'),
    re.compile(r'^FILL_?IN$', re.I),
    re.compile(r'^<REQUIRED>$', re.I),
    re.compile(r'^PLACEHOLDER$', re.I),
]


def is_placeholder(value: str) -> bool:
    """Return True if *value* looks like an unfilled placeholder."""
    stripped = value.strip()
    return any(p.match(stripped) for p in _PLACEHOLDER_PATTERNS)


def find_placeholders(env: Dict[str, str]) -> Dict[str, str]:
    """Return a dict of key -> value for every entry that is a placeholder."""
    return {k: v for k, v in env.items() if is_placeholder(v)}


def placeholder_keys(env: Dict[str, str]) -> List[str]:
    """Return a sorted list of keys whose values are placeholders."""
    return sorted(find_placeholders(env).keys())


def has_placeholders(env: Dict[str, str]) -> bool:
    """Return True if any value in *env* is a placeholder."""
    return any(is_placeholder(v) for v in env.values())


def placeholder_report(env: Dict[str, str]) -> str:
    """Return a human-readable report of placeholder keys."""
    found = find_placeholders(env)
    if not found:
        return "No placeholders found."
    lines = ["Placeholder values detected:"]
    for key, val in sorted(found.items()):
        lines.append(f"  {key}={val}")
    return "\n".join(lines)
