"""Redaction utilities for masking sensitive env values in output."""

import re
from typing import Dict, List, Optional

# Default patterns that indicate a value should be redacted
DEFAULT_SENSITIVE_PATTERNS: List[str] = [
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*PASSWD.*",
    r".*API_KEY.*",
    r".*TOKEN.*",
    r".*PRIVATE.*",
    r".*CREDENTIAL.*",
    r".*AUTH.*",
]

REDACT_PLACEHOLDER = "***REDACTED***"


def is_sensitive_key(
    key: str,
    patterns: Optional[List[str]] = None,
    case_sensitive: bool = False,
) -> bool:
    """Return True if the key matches any sensitive pattern."""
    if patterns is None:
        patterns = DEFAULT_SENSITIVE_PATTERNS
    flags = 0 if case_sensitive else re.IGNORECASE
    return any(re.fullmatch(p, key, flags=flags) for p in patterns)


def redact_value(
    value: str,
    reveal_chars: int = 0,
    placeholder: str = REDACT_PLACEHOLDER,
) -> str:
    """Return a redacted representation of value.

    Args:
        value: The original secret value.
        reveal_chars: Number of trailing characters to reveal (useful for
            confirming which secret is set without exposing the full value).
        placeholder: The string to use as the masked portion.
    """
    if not value:
        return placeholder
    if reveal_chars > 0 and len(value) > reveal_chars:
        return placeholder + value[-reveal_chars:]
    return placeholder


def redact_env(
    env: Dict[str, str],
    patterns: Optional[List[str]] = None,
    reveal_chars: int = 0,
    placeholder: str = REDACT_PLACEHOLDER,
) -> Dict[str, str]:
    """Return a copy of env with sensitive values redacted.

    Non-sensitive keys are passed through unchanged.
    """
    result: Dict[str, str] = {}
    for key, value in env.items():
        if is_sensitive_key(key, patterns=patterns):
            result[key] = redact_value(value, reveal_chars=reveal_chars, placeholder=placeholder)
        else:
            result[key] = value
    return result


def list_sensitive_keys(
    env: Dict[str, str],
    patterns: Optional[List[str]] = None,
) -> List[str]:
    """Return a sorted list of keys in env that are considered sensitive."""
    return sorted(k for k in env if is_sensitive_key(k, patterns=patterns))
